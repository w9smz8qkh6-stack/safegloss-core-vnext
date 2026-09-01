"""Generate a minimal CycloneDX SBOM for the installed release environment."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path


def component(distribution: importlib.metadata.Distribution) -> dict[str, str]:
    """Return a public package component without environment-specific paths."""
    metadata = distribution.metadata
    name = metadata["Name"]
    return {
        "type": "library",
        "name": name,
        "version": distribution.version,
        "purl": f"pkg:pypi/{name.lower()}@{distribution.version}",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    components = sorted(
        (component(distribution) for distribution in importlib.metadata.distributions()),
        key=lambda item: item["name"].lower(),
    )
    document = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:00000000-0000-0000-0000-000000000000",
        "version": 1,
        "components": components,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
