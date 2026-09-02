# ADR-0004: Stage the successor identity root as a dormant package

- Status: Accepted
- Date: 2026-09-02

## Context

The current application uses `accounts.User`, whose integer identity, role,
language preference, and current application migration history are coupled.
The planned Core/Commercial boundary needs a small shared identity root before
profile, organization, entitlement, authentication, or data-cutover work can
be designed safely. Changing `AUTH_USER_MODEL` inside the running composition
would combine schema design with a compatibility-sensitive data migration.

## Decision

Core distributes a dormant Django app named `safegloss_core_identity`. Its
first migration creates a namespaced UUID user table with email as the login
identifier, optional display name, Django authentication flags and permission
relations, and no legacy profile or role fields. Its migration graph depends
only on Django auth. Stable table and unique-constraint names form part of the
schema contract.

The default settings do not install the app and continue to select
`accounts.User`. Isolated settings and PostgreSQL 16 CI prove the successor
model and migration independently, including reverse/replay and wheel/sdist
installation. The existing PostgreSQL 17 application checks remain intact.
Django is pinned to `5.2.17` so this contract is tested against one reviewed
patch release rather than a moving compatible range.

## Consequences

- Shipping this package does not activate or migrate the successor identity.
- A later approved composition must deliberately select the new model before
  its first database migration.
- Legacy roles, language preferences, aliases, organizations, entitlements,
  credentials, and imported data remain outside this package.
- Future profile extraction and data migration can target stable UUID and
  namespaced schema contracts without rewriting this initial migration.
- The migration is PostgreSQL-specific because the canonical constraint name
  is established with PostgreSQL DDL; SQLite is not an acceptance substitute.

## Reconsideration conditions

Revisit this decision before activation if the shared identity boundary,
supported database, login identifier, or required cross-repository ownership
changes. Do not amend the released initial migration to absorb those changes;
use a new migration or superseding composition decision.
