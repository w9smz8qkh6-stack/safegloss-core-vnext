import json
import subprocess
import sys


def test_release_manifest_records_exact_artifact_digests(tmp_path):
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "safegloss_core-0.1.0a1-py3-none-any.whl").write_bytes(b"wheel")
    (dist / "safegloss_core-0.1.0a1.tar.gz").write_bytes(b"sdist")
    output = tmp_path / "release.json"

    subprocess.run(
        [
            sys.executable,
            "scripts/generate_release_manifest.py",
            "--version",
            "0.1.0a1",
            "--source-sha",
            "a" * 40,
            "--dist-dir",
            str(dist),
            "--output",
            str(output),
        ],
        check=True,
    )

    manifest = json.loads(output.read_text())
    assert manifest["schema"] == "safegloss.core-release-manifest/v1"
    assert manifest["tag"] == "v0.1.0a1"
    assert manifest["artifacts"]["wheel"]["sha256"] == (
        "ba59926159d2aa256eb8739b8da7e2b574b960e1202c6d624cbe981cef996c91"
    )
