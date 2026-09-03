# SafeGloss Core documentation

This is the canonical entry point for understanding SafeGloss Core without
first reading application source. Read the documents in the order below.

## Reading order

1. [Repository README](../README.md) — product purpose, public boundary,
   supported setup, and primary commands.
2. [Current development state](CURRENT_STATE.md) — lifecycle, current
   engineering and integration posture, limitations, next checkpoint, and the
   boundary between durable documentation and live verification.
3. [Public roadmap](product/ROADMAP.md) — reviewed, publicly disclosable Core
   direction and its promotion boundary from private SafeGloss-wide strategy.
4. [System architecture](architecture/SYSTEM.md) — runtime shape, domain
   ownership, request and data flows, persistence, and extension boundaries.
5. [Product workflows](product/WORKFLOWS.md) — what teachers, students, and
   operators do and how Study and Exam Mode behave.
6. [Interface standard](design/INTERFACE_STANDARD.md) — the shared accessible,
   conventional, task-first visual and interaction contract, component-choice
   rules, and WCAG conformance-claim gate.
7. [Core UI implementation](design/UI_IMPLEMENTATION.md) — local UI tokens,
   responsive behavior, and implementation review scope.
8. [Authorization model](security/AUTHORIZATION.md) and
   [security model](development/SECURITY_MODEL.md) — roles, object-level
   enforcement, trust boundaries, and explicit security limitations.
9. [Generated data model](generated/data-model.md),
   [route inventory](generated/routes.md), and
   [application inventory](generated/application-inventory.md) — exact
   structural facts derived from current source.
10. [Deployment guide](development/DEPLOYMENT.md),
   [release maintenance](development/RELEASE_MAINTENANCE.md),
   [generated configuration inventory](generated/configuration.md), and
   [generated deployment topology](generated/deployment-topology.md) —
   operator contract and repository-defined runtime topology.
11. [Commercial relationship](architecture/COMMERCIAL_RELATIONSHIP.md) — how
   this public upstream relates to the private hosted product.
12. [Decision records](decisions/) and [changelog](../CHANGELOG.md) — durable
   decisions and externally meaningful change history.

The generated/authored documentation contract is recorded in
[ADR-0002](decisions/0002-self-refreshing-documentation.md).

## Authority and freshness

Authored documents explain intent, invariants, limitations, and operational
judgment. Generated documents record facts that can be extracted safely from
the repository. Generated files carry a warning and must not be edited by hand.

Run:

```bash
python scripts/generate_documentation.py
python scripts/generate_documentation.py --check
python scripts/check_documentation_links.py
python scripts/check_documentation_updates.py
```

CI rejects generated-reference drift and implementation changes that omit a
durable documentation update. The path check cannot decide whether prose is
accurate; contributors must still compare affected authored documents with the
finished behavior as described in
[documentation maintenance](development/DOCUMENTATION_MAINTENANCE.md).

Generated references describe committed repository configuration. They do not
claim that a deployed environment is running, healthy, or configured exactly
like the repository. Live operational state must be verified by the operator.
`CURRENT_STATE.md` follows the same rule: it summarizes durable posture and
routes volatile branch, pull-request, CI, and environment facts to live checks.

## Historical material

Decision records preserve accepted decisions. Superseded plans, experiments,
and implementation notes must be labeled historical and must not override the
documents in this index.
