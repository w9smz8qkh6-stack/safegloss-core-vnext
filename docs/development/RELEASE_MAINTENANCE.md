# Core release maintenance

SafeGloss Core is pre-stable. The current release workflow is deliberately a
**dry run**, not a release or publishing command.

## Dry-run procedure

Dispatch `Release dry run` only with all of the following:

1. `dry_run=true`;
2. an exact commit SHA equal to the current merged `main` tip; and
3. a PEP 440 version equal to the version in that commit's `pyproject.toml`.

The release-preparation pull request changes the package version, changelog,
and release notes together. The initial public pre-stable candidate is
`0.1.0a1`; this preparation does not create a tag, GitHub Release, PyPI
publication, Hosted update, or deployment.

The workflow refuses an existing `vVERSION` tag, a source SHA outside `main`, a
version mismatch, and any request with `dry_run=false`. It builds a wheel and
source distribution once, installs each outside the checkout against its own
fresh PostgreSQL database, then creates checksum, CycloneDX SBOM, and GitHub
attestation evidence. It also emits the public `safegloss.core-release-manifest/v1`
record, which binds the exact source SHA, version/tag, wheel name/hash and source
distribution name/hash that a future GitHub Release must carry. It has no permission to write repository contents,
create a release, publish to a package index, update Hosted, or deploy.

## Future real-release gate

Before any workflow receives tag or GitHub Release authority, maintainers must
separately approve: the version-preparation PR, the immutable-release workflow,
SBOM/provenance retention, and recovery handling for a rejected release. That
release attaches the wheel, source distribution, checksums, SBOM and the release
manifest. It does not publish to PyPI; PyPI Trusted Publishing remains deferred.
A failed release never permits moving a tag, overwriting an artifact, or
selecting a Hosted version automatically.

GitHub describes the OIDC/`id-token: write` model for PyPI Trusted Publishing
and the permission model for artifact attestations in its official
documentation. No access token belongs in this repository.
