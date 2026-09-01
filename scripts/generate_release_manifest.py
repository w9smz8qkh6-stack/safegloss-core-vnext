#!/usr/bin/env python3
"""Write the public, immutable release-artifact manifest for one Core build."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--dist-dir", type=Path, default=Path("dist"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    artifacts = sorted(path for path in args.dist_dir.iterdir() if path.suffix in {".whl", ".gz"})
    wheel = next((path for path in artifacts if path.suffix == ".whl"), None)
    sdist = next((path for path in artifacts if path.name.endswith(".tar.gz")), None)
    if wheel is None or sdist is None:
        raise SystemExit("Expected exactly one wheel and one source distribution.")

    manifest = {
        "schema": "safegloss.core-release-manifest/v1",
        "package": "safegloss-core",
        "version": args.version,
        "tag": f"v{args.version}",
        "source_sha": args.source_sha,
        "artifacts": {
            "wheel": {"filename": wheel.name, "sha256": sha256(wheel)},
            "sdist": {"filename": sdist.name, "sha256": sha256(sdist)},
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
