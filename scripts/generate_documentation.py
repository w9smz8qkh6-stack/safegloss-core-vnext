#!/usr/bin/env python3
"""Generate deterministic architecture references from repository source.

The generated files are committed so a reader can understand the current
system without importing Django or running the application. Run this script
after changing models, routes, settings, services, commands, environment
configuration, or Compose topology. CI uses ``--check`` to reject drift.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "documentation.toml"
GENERATOR_VERSION = 1
RELATION_FIELDS = {"ForeignKey", "ManyToManyField", "OneToOneField"}
SOURCE_SUFFIXES = {".py", ".sh", ".yaml", ".yml"}
IGNORED_PARTS = {
    ".git",
    ".eggs",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "docs",
    "migrations",
    "node_modules",
    "static",
    "staticfiles",
    "templates",
    "tests",
}
ENV_PATTERNS = (
    re.compile(r"\benv(?:\.[A-Za-z_][A-Za-z0-9_]*)?\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),
    re.compile(r"\bos\.getenv\(\s*['\"]([A-Z][A-Z0-9_]*)['\"]"),
    re.compile(r"\bos\.environ(?:\.get\(\s*|\[\s*)['\"]([A-Z][A-Z0-9_]*)['\"]"),
    re.compile(r"\$\{([A-Z][A-Z0-9_]*)"),
)


@dataclass(frozen=True)
class Field:
    name: str
    kind: str
    target: str | None
    nullable: bool


@dataclass(frozen=True)
class Model:
    app: str
    name: str
    fields: tuple[Field, ...]

    @property
    def label(self) -> str:
        return f"{self.app}.{self.name}"


@dataclass(frozen=True)
class Route:
    pattern: str
    view: str
    name: str
    source: str


def load_config() -> dict[str, Any]:
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def parse(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"), filename=relative(path))


def expression(node: ast.AST | None) -> str:
    if node is None:
        return ""
    try:
        return ast.unparse(node)
    except (AttributeError, ValueError):
        return node.__class__.__name__


def literal_string(node: ast.AST | None) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def assignment_value(tree: ast.Module, name: str) -> ast.AST | None:
    for node in tree.body:
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == name:
                return node.value
    return None


def local_apps(settings_path: Path) -> list[str]:
    value = assignment_value(parse(settings_path), "INSTALLED_APPS")
    if not isinstance(value, (ast.List, ast.Tuple)):
        raise ValueError(
            "INSTALLED_APPS must be a literal list or tuple for documentation generation"
        )
    apps: list[str] = []
    for item in value.elts:
        configured = literal_string(item)
        if not configured:
            continue
        candidate = configured.split(".", 1)[0]
        if (ROOT / candidate).is_dir() and candidate not in apps:
            apps.append(candidate)
    return apps


def auth_user_label(settings_path: Path) -> str:
    value = assignment_value(parse(settings_path), "AUTH_USER_MODEL")
    return literal_string(value) or "auth.User"


def call_name(call: ast.Call) -> str:
    return expression(call.func).split(".")[-1]


def relation_target(node: ast.AST, *, app: str, model: str, auth_user: str) -> str:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        target = node.value
        if target.lower() == "self":
            return f"{app}.{model}"
        return target if "." in target else f"{app}.{target}"
    rendered = expression(node)
    if rendered == "settings.AUTH_USER_MODEL":
        return auth_user
    if "." not in rendered:
        return f"{app}.{rendered}"
    return rendered


def discover_models(apps: list[str], auth_user: str) -> tuple[list[Model], list[Path]]:
    models: list[Model] = []
    sources: list[Path] = []
    for app in apps:
        modules = sorted((ROOT / app).glob("models*.py"))
        for module in modules:
            sources.append(module)
            tree = parse(module)
            for node in tree.body:
                if not isinstance(node, ast.ClassDef):
                    continue
                fields: list[Field] = []
                model_base = any(
                    expression(base).endswith(("Model", "AbstractUser")) for base in node.bases
                )
                for statement in node.body:
                    if not isinstance(statement, (ast.Assign, ast.AnnAssign)):
                        continue
                    value = statement.value
                    if not isinstance(value, ast.Call):
                        continue
                    kind = call_name(value)
                    if not (kind.endswith("Field") or kind in RELATION_FIELDS):
                        continue
                    if isinstance(statement, ast.Assign):
                        names = [
                            target.id
                            for target in statement.targets
                            if isinstance(target, ast.Name)
                        ]
                    else:
                        names = (
                            [statement.target.id] if isinstance(statement.target, ast.Name) else []
                        )
                    if not names:
                        continue
                    keywords = {
                        keyword.arg: keyword.value for keyword in value.keywords if keyword.arg
                    }
                    nullable = isinstance(keywords.get("null"), ast.Constant) and bool(
                        keywords["null"].value
                    )
                    target = None
                    if kind in RELATION_FIELDS and value.args:
                        target = relation_target(
                            value.args[0], app=app, model=node.name, auth_user=auth_user
                        )
                    for name in names:
                        fields.append(Field(name=name, kind=kind, target=target, nullable=nullable))
                if model_base or fields:
                    models.append(Model(app=app, name=node.name, fields=tuple(fields)))
    return sorted(models, key=lambda item: (item.app, item.name)), sources


def module_path(module: str) -> Path:
    return ROOT / Path(*module.split(".")).with_suffix(".py")


def include_spec(call: ast.Call) -> tuple[str | None, str | None]:
    if not isinstance(call.func, ast.Name) or call.func.id != "include" or not call.args:
        return None, None
    namespace = None
    for keyword in call.keywords:
        if keyword.arg == "namespace":
            namespace = literal_string(keyword.value)
    return literal_string(call.args[0]), namespace


def module_app_name(module: str) -> str | None:
    path = module_path(module)
    if not path.exists():
        return None
    return literal_string(assignment_value(parse(path), "app_name"))


def discover_routes(root_module: str) -> tuple[list[Route], list[Path]]:
    routes: list[Route] = []
    sources: set[Path] = set()

    def visit(
        module: str,
        prefix: str = "",
        stack: tuple[str, ...] = (),
        namespace: str = "",
    ) -> None:
        path = module_path(module)
        if not path.exists() or module in stack:
            return
        sources.add(path)
        tree = parse(path)
        value = assignment_value(tree, "urlpatterns")
        if not isinstance(value, (ast.List, ast.Tuple)):
            return
        for item in value.elts:
            if not isinstance(item, ast.Call) or call_name(item) not in {"path", "re_path"}:
                continue
            pattern = literal_string(item.args[0]) if item.args else None
            pattern = (
                pattern if pattern is not None else expression(item.args[0] if item.args else None)
            )
            full_pattern = f"/{prefix}{pattern}".replace("//", "/")
            view_node = item.args[1] if len(item.args) > 1 else None
            name = ""
            for keyword in item.keywords:
                if keyword.arg == "name":
                    name = literal_string(keyword.value) or expression(keyword.value)
            qualified_name = f"{namespace}:{name}" if namespace and name else name
            if isinstance(view_node, ast.Call):
                nested, explicit_namespace = include_spec(view_node)
                if nested:
                    nested_path = module_path(nested)
                    if nested_path.exists():
                        nested_namespace = explicit_namespace or module_app_name(nested) or ""
                        qualified_namespace = ":".join(
                            part for part in (namespace, nested_namespace) if part
                        )
                        visit(
                            nested,
                            f"{prefix}{pattern}",
                            (*stack, module),
                            qualified_namespace,
                        )
                    else:
                        routes.append(
                            Route(
                                full_pattern,
                                f"include({nested})",
                                qualified_name,
                                relative(path),
                            )
                        )
                    continue
            routes.append(
                Route(full_pattern, expression(view_node), qualified_name, relative(path))
            )

    visit(root_module)
    return sorted(routes, key=lambda item: (item.pattern, item.source, item.name)), sorted(sources)


def service_sources(apps: list[str]) -> list[Path]:
    selected: set[Path] = set()
    names = {"access.py", "jobs.py", "middleware.py", "permissions.py", "services.py", "signals.py"}
    for app in apps:
        root = ROOT / app
        for path in root.rglob("*.py"):
            if "migrations" in path.parts or "tests" in path.parts:
                continue
            if path.name in names or "services" in path.parts:
                selected.add(path)
    return sorted(selected)


def public_declarations(path: Path) -> list[tuple[str, str, str]]:
    declarations: list[tuple[str, str, str]] = []
    for node in parse(path).body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name.startswith("_"):
            continue
        kind = "class" if isinstance(node, ast.ClassDef) else "function"
        summary = (ast.get_docstring(node) or "").strip().splitlines()[0:1]
        declarations.append((kind, node.name, summary[0] if summary else ""))
    return declarations


def management_commands(apps: list[str]) -> list[Path]:
    commands: list[Path] = []
    for app in apps:
        directory = ROOT / app / "management" / "commands"
        if directory.exists():
            commands.extend(path for path in directory.glob("*.py") if path.name != "__init__.py")
    return sorted(commands)


def configuration_sources() -> list[Path]:
    sources: list[Path] = []
    for path in ROOT.rglob("*"):
        ignored = any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts)
        if not path.is_file() or ignored:
            continue
        selected = (
            path.suffix in SOURCE_SUFFIXES
            or path.name.startswith("Dockerfile")
            or path.name == ".env.example"
        )
        if selected:
            sources.append(path)
    return sorted(sources)


def environment_inventory(paths: list[Path]) -> dict[str, list[str]]:
    variables: dict[str, set[str]] = defaultdict(set)
    for path in paths:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in ENV_PATTERNS:
            for match in pattern.finditer(content):
                variables[match.group(1)].add(relative(path))
        if path.name == ".env.example":
            for line in content.splitlines():
                match = re.match(r"^([A-Z][A-Z0-9_]*)=", line.strip())
                if match:
                    variables[match.group(1)].add(relative(path))
    return {name: sorted(paths) for name, paths in sorted(variables.items())}


def compose_services(path: Path) -> dict[str, dict[str, Any]]:
    services: dict[str, dict[str, Any]] = {}
    in_services = False
    current: str | None = None
    in_depends = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line:
            continue
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 0:
            in_services = stripped == "services:"
            current = None
            in_depends = False
            continue
        if not in_services:
            continue
        if indent == 2 and stripped.endswith(":"):
            current = stripped[:-1]
            services[current] = {"depends_on": [], "image": "", "build": False}
            in_depends = False
            continue
        if current is None:
            continue
        if indent == 4 and stripped == "depends_on:":
            in_depends = True
            continue
        if indent == 4:
            in_depends = False
            if stripped.startswith("image:"):
                services[current]["image"] = stripped.split(":", 1)[1].strip().strip("'\"")
            elif stripped.startswith("build:"):
                services[current]["build"] = True
            continue
        if in_depends and indent >= 6:
            dependency = stripped.split(":", 1)[0].lstrip("- ")
            if dependency and dependency not in {"condition", "required", "restart"}:
                services[current]["depends_on"].append(dependency)
    return services


def entity_id(label: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", label)


def model_target_label(target: str, *, app: str) -> str:
    return target if "." in target else f"{app}.{target}"


def render_application(
    project: str,
    apps: list[str],
    models: list[Model],
    services: list[Path],
    commands: list[Path],
) -> str:
    model_counts = defaultdict(int)
    dependencies: set[tuple[str, str]] = set()
    for model in models:
        model_counts[model.app] += 1
        for field in model.fields:
            if not field.target:
                continue
            target_app = model_target_label(field.target, app=model.app).split(".", 1)[0]
            if target_app in apps and target_app != model.app:
                dependencies.add((model.app, target_app))
    lines = [
        "<!-- Generated by scripts/generate_documentation.py; do not edit. -->",
        "# Generated application inventory",
        "",
        f"This reference is generated from the current {project} repository.",
        "",
        "## Component relationships",
        "",
        "```mermaid",
        "flowchart LR",
    ]
    for app in apps:
        lines.append(f'  {entity_id(app)}["{app}"]')
    for source, target in sorted(dependencies):
        lines.append(f"  {entity_id(source)} --> {entity_id(target)}")
    if not dependencies:
        lines.append("  repository[No cross-app model relationships detected]")
    lines.extend(
        [
            "```",
            "",
            "## Django applications",
            "",
            "| Application | Models |",
            "|---|---:|",
        ]
    )
    for app in apps:
        lines.append(f"| `{app}` | {model_counts[app]} |")
    lines.extend(["", "## Service modules", ""])
    if services:
        for path in services:
            declarations = public_declarations(path)
            names = (
                ", ".join(f"`{name}`" for _, name, _ in declarations) or "No public declarations"
            )
            lines.append(f"- `{relative(path)}` — {names}")
    else:
        lines.append("No service modules were detected.")
    lines.extend(["", "## Management commands", ""])
    if commands:
        lines.extend(f"- `{path.stem}` (`{relative(path)}`)" for path in commands)
    else:
        lines.append("No project management commands were detected.")
    return "\n".join(lines) + "\n"


def render_models(project: str, models: list[Model]) -> str:
    lines = [
        "<!-- Generated by scripts/generate_documentation.py; do not edit. -->",
        "# Generated data model",
        "",
        f"This field and relationship inventory is generated from {project} model declarations.",
        "It describes repository structure, not production row counts or live data.",
        "",
        "## Relationship diagram",
        "",
        "```mermaid",
        "classDiagram",
        "direction LR",
    ]
    labels = {model.label for model in models}
    for model in models:
        lines.append(f'  class {entity_id(model.label)}["{model.label}"]')
    external: set[str] = set()
    relations: list[tuple[str, str, str, str]] = []
    for model in models:
        for field in model.fields:
            if not field.target:
                continue
            target = model_target_label(field.target, app=model.app)
            if target not in labels:
                external.add(target)
            relations.append((model.label, target, field.name, field.kind))
    for target in sorted(external):
        lines.append(f'  class {entity_id(target)}["{target}"]')
    for source, target, field, kind in sorted(relations):
        arrow = "-->" if kind != "ManyToManyField" else "--"
        lines.append(f"  {entity_id(source)} {arrow} {entity_id(target)} : {field}")
    lines.extend(["```", ""])
    current_app = None
    for model in models:
        if model.app != current_app:
            current_app = model.app
            lines.extend([f"## `{current_app}`", ""])
        lines.extend(
            [
                f"### `{model.label}`",
                "",
                "| Field | Type | Relation target | Database null allowed |",
                "|---|---|---|---|",
            ]
        )
        if model.fields:
            for field in model.fields:
                target = f"`{field.target}`" if field.target else "—"
                lines.append(
                    f"| `{field.name}` | `{field.kind}` | {target} | "
                    f"{'yes' if field.nullable else 'no'} |"
                )
        else:
            lines.append("| — | Inherited fields only | — | — |")
        lines.append("")
    return "\n".join(lines)


def render_routes(project: str, routes: list[Route]) -> str:
    lines = [
        "<!-- Generated by scripts/generate_documentation.py; do not edit. -->",
        "# Generated route inventory",
        "",
        f"Routes are resolved statically from the {project} root URL configuration.",
        "Third-party includes are shown as include boundaries.",
        "",
        "| URL pattern | Name | View or include | Declared in |",
        "|---|---|---|---|",
    ]
    for route in routes:
        lines.append(f"| `{route.pattern}` | `{route.name}` | `{route.view}` | `{route.source}` |")
    return "\n".join(lines) + "\n"


def render_configuration(project: str, variables: dict[str, list[str]]) -> str:
    lines = [
        "<!-- Generated by scripts/generate_documentation.py; do not edit. -->",
        "# Generated configuration inventory",
        "",
        f"Environment-variable names are detected from current {project} source and "
        "deployment files.",
        "Values are intentionally never read or rendered. Requiredness and operational "
        "meaning remain",
        "documented in the authored deployment guide and `.env.example`.",
        "",
        "| Variable | Referenced by |",
        "|---|---|",
    ]
    for name, paths in variables.items():
        sources = ", ".join(f"`{path}`" for path in paths)
        lines.append(f"| `{name}` | {sources} |")
    return "\n".join(lines) + "\n"


def render_compose(project: str, compose: dict[Path, dict[str, dict[str, Any]]]) -> str:
    lines = [
        "<!-- Generated by scripts/generate_documentation.py; do not edit. -->",
        "# Generated deployment topology",
        "",
        f"These diagrams are generated from the Compose definitions committed to {project}.",
        "They do not assert that a particular environment is running or healthy.",
        "",
    ]
    for path, services in compose.items():
        lines.extend([f"## `{relative(path)}`", "", "```mermaid", "flowchart LR"])
        for name, details in services.items():
            descriptor = details["image"] or ("local build" if details["build"] else "service")
            safe_descriptor = descriptor.replace('"', "'")
            lines.append(f'  {entity_id(name)}["{name}<br/>{safe_descriptor}"]')
        for name, details in services.items():
            for dependency in sorted(set(details["depends_on"])):
                if dependency in services:
                    lines.append(f"  {entity_id(name)} --> {entity_id(dependency)}")
        lines.extend(["```", "", "| Service | Image/build | Depends on |", "|---|---|---|"])
        for name, details in services.items():
            descriptor = details["image"] or ("local build" if details["build"] else "—")
            dependencies = (
                ", ".join(f"`{item}`" for item in sorted(set(details["depends_on"]))) or "—"
            )
            lines.append(f"| `{name}` | `{descriptor}` | {dependencies} |")
        lines.append("")
    return "\n".join(lines)


def build_outputs(config: dict[str, Any]) -> dict[Path, str]:
    project = config["project_name"]
    generated = ROOT / config["generated_directory"]
    settings_path = ROOT / config["settings_path"]
    apps = local_apps(settings_path)
    models, model_sources = discover_models(apps, auth_user_label(settings_path))
    root_module = config["root_urlconf"].removesuffix(".py").replace("/", ".")
    routes, route_sources = discover_routes(root_module)
    services = service_sources(apps)
    commands = management_commands(apps)
    config_sources = configuration_sources()
    variables = environment_inventory(config_sources)
    contributing_config_sources = {
        ROOT / source for paths in variables.values() for source in paths
    }
    compose_paths = [ROOT / item for item in config.get("compose_files", [])]
    compose = {path: compose_services(path) for path in compose_paths}
    outputs = {
        generated / "application-inventory.md": render_application(
            project, apps, models, services, commands
        ),
        generated / "data-model.md": render_models(project, models),
        generated / "routes.md": render_routes(project, routes),
        generated / "configuration.md": render_configuration(project, variables),
        generated / "deployment-topology.md": render_compose(project, compose),
    }
    manifest_path = generated / "manifest.json"
    inventory = {
        "generator_version": GENERATOR_VERSION,
        "project": project,
        "inputs": sorted(
            {
                relative(CONFIG_PATH),
                "scripts/generate_documentation.py",
                relative(settings_path),
                *(relative(path) for path in model_sources),
                *(relative(path) for path in route_sources),
                *(relative(path) for path in services),
                *(relative(path) for path in commands),
                *(relative(path) for path in compose_paths),
                *(relative(path) for path in contributing_config_sources),
            }
        ),
        "outputs": sorted([*(relative(path) for path in outputs), relative(manifest_path)]),
    }
    normalized = "".join(
        f"{relative(path)}\0{content}\0" for path, content in sorted(outputs.items())
    )
    inventory["generated_content_sha256"] = hashlib.sha256(normalized.encode()).hexdigest()
    outputs[manifest_path] = json.dumps(inventory, indent=2, sort_keys=True) + "\n"
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if committed generated documentation differs from current source.",
    )
    args = parser.parse_args()
    try:
        outputs = build_outputs(load_config())
    except (OSError, SyntaxError, ValueError) as exc:
        print(f"Documentation generation failed: {exc}", file=sys.stderr)
        return 2

    stale: list[str] = []
    for path, content in outputs.items():
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            stale.append(relative(path))
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")

    if args.check and stale:
        print("Generated documentation is stale. Run: python scripts/generate_documentation.py")
        for path in stale:
            print(f"  - {path}")
        return 1
    if stale:
        print("Refreshed generated documentation:")
        for path in stale:
            print(f"  - {path}")
    else:
        print("Generated documentation is current.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
