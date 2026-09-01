# Changelog

All notable changes to SafeGloss Core will be recorded here.

The project follows semantic versioning after the first stable release. During alpha, minor releases may contain schema or interface changes documented in release notes.

## Unreleased

### Added

- Added an installable SafeGloss Core source/wheel distribution with a
  `safegloss-core` management command, package-owned Django assets, and CI
  proof that clean PostgreSQL self-hosting works from both artifact formats.
- Added a dry-run-only release-verification workflow that creates checksums,
  CycloneDX SBOM evidence, and artifact attestations while refusing tags,
  releases, package publication, Hosted changes, and deployment.

### Changed

- Added a canonical documentation reading path, authored system architecture,
  product workflows, authorization model, and public Commercial-relationship
  guide so the product can be understood without first scanning source.
- Added deterministic, source-derived application, data-model, route,
  configuration, and Compose-topology references with Mermaid diagrams. CI now
  rejects stale generated documentation, while standing rules continue to
  require semantic updates to authored documentation.
- Added a canonical current-development-state record and made it part of
  repository orientation and change review. It summarizes durable lifecycle,
  integration, delivery, and limitation context while requiring volatile Git,
  CI, PR, and environment facts to be verified live.
- Added a filtered public Core roadmap with explicit Now/Next/Later/Exploring
  semantics and a disclosure gate from the private SafeGloss-wide strategy
  system. Proposals remain distinct from maintainer-approved commitments.
- Added a canonical interface standard for WCAG 2.2 Level AA targeting,
  conventional task-based component selection, visual-system consistency,
  workflow states, mandatory continuous responsiveness across representative
  phone, laptop, and desktop viewports, evidence-backed conformance claims, and
  a traceable screenshot exchange between automated testing and UI review.
- Made documentation review and updates part of completion for every implementation,
  behavior, interface, test, script, dependency, configuration, security, deployment,
  operations, architecture, and user-visible change.
- Added a lightweight documentation handoff check. It verifies that implementation
  diffs include a durable documentation path while leaving semantic accuracy to the
  required implementation-to-document comparison.
- Established a standing cadence to commit and push task-owned, verified Core changes
  at cohesive green checkpoints and task completion. Production delivery remains a
  separate reviewed Core-to-Hosted integration step.
- Clarified that protected `main` changes use scoped task branches, pull requests, and
  required checks; administrator bypass is not part of the standing cadence.
- Made generated-documentation discovery ignore local build outputs, keeping
  committed references reproducible in clean CI checkouts.

## 0.1.0 - 2026-08-15

### Added

- Clean public-core Django application.
- Email-based teacher and student accounts.
- Courses, rosters, enrollment, and join codes.
- Multilingual glossary, term, and translation models.
- Study Mode, manual Exam Mode, and scheduled Exam Mode.
- CSV import/export and print-friendly student views.
- Public contributor, security, support, and architecture documentation.
