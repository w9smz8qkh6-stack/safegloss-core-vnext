# Current development state

This is the canonical orientation record for SafeGloss Core's durable
development state. Read it after the repository README and before detailed
architecture or workflow documents. It summarizes the repository snapshot that
contains it; source, migrations, tests, generated references, and the focused
documents linked from `docs/README.md` remain authoritative for their specific
contracts.

## Product and lifecycle

- SafeGloss Core is the public, vendor-neutral, independently self-hostable
  upstream for glossary and exam-access support.
- The project is pre-stable and currently uses the `0.1.x` development line.
- Teachers manage courses, rosters, glossaries, translations, Study Mode, and
  Exam Mode. Students use assigned bilingual vocabulary in their configured
  language.
- PostgreSQL is the canonical database. Python 3.12 and newer are supported by
  the repository's current quality gates.
- Core has no maintainer-operated production deployment target. A self-hoster
  is responsible for its environment, secrets, backups, upgrades, monitoring,
  and recovery.

## Repository and integration posture

- This is the public Core-vNext successor candidate, seeded from the annotated
  `legacy-baseline-2026-09-01` snapshot. It has no production deployment
  target and its local lab uses isolated named volumes and loopback-only ports.
- Core owns functionality that is safe for a public, provider-neutral product.
  Billing, hosted-provider integrations, behavioral analytics, private
  research operations, and customer data do not belong here.
- SafeGloss Commercial is the private production downstream. Shared public
  behavior is developed and reviewed in Core first, then integrated using the
  Commercial repository's Core-upstream procedure.
- The repository contains canonical authored product, architecture,
  authorization, deployment, and boundary documentation plus deterministic
  source-generated application, model, route, configuration, and Compose
  references.
- `docs/product/ROADMAP.md` is the filtered public projection of reviewed Core
  direction. The private Commercial strategy system retains the complete
  SafeGloss-wide idea and prioritization record.
- Protected-branch delivery uses a scoped branch, required CI, linear history,
  resolved conversations, and no force-push or deletion. The current GitHub
  rule does not require a separate approving review; standing delivery rules do
  not permit bypassing any configured gate.

## Known limitations and invariants

- Exam Mode restricts application content; it is not a secure browser,
  proctoring system, or operating-system lockdown.
- Authorization is enforced server-side and must remain covered by tests.
- Generated inventories describe committed structure. They do not establish
  the health, configuration, or version of a running installation.
- Core must remain free of credentials, production/customer/research data,
  curriculum source files, provider payloads, and Commercial-only code.

## Active work and next checkpoint

The non-secret vNext bootstrap is complete: scoped-branch CI,
protected-main controls, and an empty/synthetic local-lab smoke test passed on
2026-09-01. The test used ephemeral generated secrets, a vNext-only database
volume/network, and loopback access, then removed every disposable resource.
Core packaging establishes an installable artifact with package-owned
templates/static assets and verifies wheel and source-distribution self-hosting
against PostgreSQL in the dedicated CI package job. A dormant, independently
migratable `safegloss_core_identity` package now stages the successor
email-login UUID identity root and is verified from source, wheel, and sdist on
PostgreSQL 16. It is not installed by the default settings, which still select
`accounts.User`; no current account or application behavior has been migrated.
The successor first needs its catalogue foundation and then its profile and
membership layers; assembled composition and data migration remain later,
separately reviewed checkpoints. The active release work is
dry-run-only: it verifies source/version/tag refusal rules, artifacts,
checksums, SBOM and provenance evidence without a tag, GitHub Release, PyPI
configuration/upload, Hosted action, or production transition. Those remain
separate accepted work packages. A protected release-preparation PR must first
align the initial `0.1.0a1` version, changelog, and release notes before the
manual dry run can execute. Do not infer current branch,
pull request, CI, or lab state from this file; verify it live.

Use repository evidence for the active development position:

```bash
git status -sb
git log -1 --oneline
gh pr status
```

Use the quality gates in `README.md` to establish implementation health. A
clean working tree or green historical run does not prove current deployment
health, and Core has no repository-authorized production target to inspect.

## Maintenance contract

Update this record when a change materially alters product maturity, supported
runtime/database posture, repository ownership, Core/Commercial boundaries,
delivery or deployment posture, important limitations, the durable active
workstream, or its next integration checkpoint. Ordinary fixes do not require
a wording change when every claim remains accurate.

Agents and contributors must begin orientation through `docs/README.md`, read
this record and the public roadmap for product-planning work, then follow their
links to the governing documents and perform the live checks relevant to the
task. Automation can require that documentation was considered, but reviewers
remain responsible for deciding whether this summary changed by meaning.
