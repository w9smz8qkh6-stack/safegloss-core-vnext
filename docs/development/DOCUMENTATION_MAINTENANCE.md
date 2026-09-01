# Documentation maintenance

Documentation is part of the SafeGloss Core definition of done. Every task that
changes source code, behavior, interfaces, tests, scripts, dependencies,
configuration, security, deployment, operations, architecture, or
user-visible output must review and update the relevant durable documentation
in that same task. Contributors do not wait for a separate documentation
request.

## Documentation map

Identify the records that govern the changed area before editing:

- `docs/README.md` for the canonical reading order, authority, and freshness
  contract;
- `docs/CURRENT_STATE.md` for durable lifecycle, engineering/integration
  posture, limitations, active workstream, and next checkpoint; use live Git,
  PR, CI, and operator evidence for volatile status;
- `docs/product/ROADMAP.md` for reviewed public Core direction, outcomes,
  horizons, dependencies, success signals, and the private-strategy disclosure
  boundary;
- `README.md` for public scope, features, setup, supported environments, data
  formats, and primary quality gates;
- `docs/architecture/SYSTEM.md`, `docs/product/WORKFLOWS.md`, and
  `docs/security/AUTHORIZATION.md` for architecture, domain intent, data flows,
  product behavior, roles, and enforcement;
- `docs/generated/` for source-derived application, model, route,
  configuration, and Compose topology facts;
- `CONTRIBUTING.md` and `AGENTS.md` for contributor and agent workflow;
- `.env.example` and `docs/development/DEPLOYMENT.md` for configuration and
  operator setup;
- `SECURITY.md` and `docs/development/SECURITY_MODEL.md` for security, privacy,
  trust boundaries, and Exam Mode limitations;
- public UI help and documented CSV or other interfaces for user-visible
  contracts;
- `docs/decisions/` for durable architectural and repository-boundary
  decisions; and
- `CHANGELOG.md` for externally meaningful changes and release history.

## Completion procedure

1. Inspect the finished implementation, tests, configuration, and observed
   behavior, then compare every governing document by meaning rather than by
   timestamp, filename, or keyword.
2. Update affected setup instructions, architecture, operational runbooks,
   public contracts and data formats, security and privacy guidance, user
   documentation, and changelog entries.
3. Update `docs/CURRENT_STATE.md`, capability, workstream, and decision records
   whenever their durable claims or status change. Do not copy volatile branch,
   pull-request, CI, or deployment state into prose when it can be verified
   live. Add or amend an ADR for a durable architectural decision.
4. If repository-owned tooling can safely regenerate facts, schemas,
   inventories, or indexes, use it and review the generated diff. Passing
   freshness, generation, link, or path checks is evidence only; it does not
   prove that explanatory documentation is accurate.
5. Run the documentation handoff check and all affected repository quality
   gates. Report changed documents and verification results explicitly.

Run `python scripts/check_documentation_updates.py` locally. CI runs the same
diff-based check. It fails when implementation paths change without a durable
documentation path, but semantic completeness remains the contributor's and
reviewer's responsibility.

Run `python scripts/generate_documentation.py` whenever models, routes,
settings, service boundaries, management commands, environment-variable use,
or Compose topology may have changed. Commit the regenerated files and verify
them with `python scripts/generate_documentation.py --check`. CI performs the
same deterministic check. A passing generator proves only that extracted facts
are current; it cannot explain intent or determine whether authored prose is
semantically complete.

The generator deliberately excludes local build and packaging outputs (such as
`build/` and `.eggs/`) so its results describe the committed source tree and
remain identical in a clean CI checkout.

Never hand-edit `docs/generated/`. Change the source or generator, regenerate,
and review the result. Generated topology describes committed configuration,
not live deployment health or provider state.

Run `python scripts/check_documentation_links.py` after changing documentation
structure. It validates repository-local links and ensures generated Markdown
retains its ownership marker.

`docs/CURRENT_STATE.md` must change when product maturity, supported runtimes or
database posture, repository ownership, the Core/Commercial boundary, delivery
or deployment posture, important limitations, the durable active workstream,
or the next integration checkpoint changes by meaning. Review it for every
such change even when no automated path rule can establish semantic impact.
Ordinary implementation changes do not require an edit when all of its claims
remain accurate.

Update the public roadmap when an approved Core initiative changes horizon,
outcome, dependencies, success or learning signal, public ownership, or
delivery status. Public proposals and issue discussion do not authorize roadmap
promotion. Never import private Commercial, provider, customer, research,
analytics, billing, or operational context; copy only a reviewed,
vendor-neutral public projection and preserve Core-first integration order.
Run `python scripts/check_strategy_records.py` after changing the public
roadmap; CI validates stable initiative IDs and roadmap table shape.

## Cross-repository and incomplete work

Core is the public, vendor-neutral upstream of the private SafeGloss Hosted
application. When a Core change affects Hosted integration, deployment,
operations, architecture, or user-facing behavior, update Hosted's canonical
documentation in the original task. The converse applies when Hosted work
changes a public Core contract. Keep repository edits and verification
separate and report the Core-to-Hosted integration order.

If an affected repository is unavailable, overlapping work prevents a safe
edit, or a required fact cannot be verified, the task is incomplete. Name the
repository, exact missing or inaccurate document, unresolved fact, and blocker
in the handoff.

Documentation completion is a prerequisite for Core's standing delivery
cadence. After relevant checks pass, commit task-owned changes and push the
current branch to its existing configured upstream at a cohesive green
checkpoint and task completion. Local edits, commits, pushes, and Hosted
integration remain distinct checked steps. Never include unrelated dirty work,
force-push, rewrite history, bypass branch protection, expose secrets, or
proceed past failed checks. Core itself has no production deployment target;
reviewed Core changes reach production only through the documented Hosted
integration flow.

Core's protected `main` uses scoped task branches and pull requests. Required
checks must pass before merge, and the standing cadence does not waive a
required human approval or permit administrator bypass.
