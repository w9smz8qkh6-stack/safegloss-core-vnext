# Vendor-neutral deployment

SafeGloss Core is a WSGI Django application backed by PostgreSQL. The included Dockerfile runs Gunicorn as an unprivileged user and serves collected static assets through WhiteNoise.

## Required production configuration

- `DJANGO_SECRET_KEY`: a long random value stored in a secret manager;
- `DATABASE_URL`: a PostgreSQL connection URL;
- `ALLOWED_HOSTS`: comma-separated public hostnames;
- `DEBUG=False`; and
- TLS termination at the reverse proxy or platform edge.

Set `SECURE_SSL_REDIRECT=True` after proxy headers and HTTPS behavior have been verified. Enable HSTS subdomains and preload only when every affected hostname is permanently HTTPS-capable.

## Artifact-based self-hosting

Core artifacts can be built with `python -m build` and installed with
`python -m pip install <artifact>`. After installation, the `safegloss-core` command
is the equivalent of `python manage.py`; it configures the same Django settings
module. Set `STATIC_ROOT` to an operator-writable deployment location before
running `safegloss-core collectstatic --noinput`.

The distribution contains Django configuration, migrations, templates, and
static source assets. It does not include a database, media uploads, secrets,
or any Hosted implementation. Package-index publication and Hosted version
selection are intentionally outside this initial artifact contract.

The artifact also contains `safegloss_core_identity`, a dormant successor
identity app. The packaged `safegloss-core` command continues to load the
default settings and `accounts.User`, so ordinary installation and migration do
not create or activate successor identity tables. Selecting the staged app
requires a separately reviewed settings composition and data-migration plan;
self-hosters must not switch `AUTH_USER_MODEL` in an established database.

## Release sequence

1. Back up the PostgreSQL database.
2. Build an immutable image from a reviewed tag.
3. Run `safegloss-core check --deploy` with production configuration.
4. Run `safegloss-core migrate --noinput` as a one-off release task.
5. Start the web process.
6. Confirm `/health/`, login, and an authorized glossary view.

Do not run migrations independently from every replica during a rolling deployment.

## Persistent data

PostgreSQL is the only persistent service in the first public core. Back it up using the operator's normal PostgreSQL tools and test restores regularly. The project does not ship a production backup scheduler.

## Rollback

Application rollback means redeploying the prior image. Database rollback depends on the migrations in the release; review each migration before deployment and retain a tested backup when a migration is not safely reversible.
