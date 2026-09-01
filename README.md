# SafeGloss Core

SafeGloss Core is a self-hosted multilingual glossary and exam-access support application for schools. Teachers create subject glossaries, connect them to courses, and give each learner a preferred translation language. During Exam Mode, students see only approved bilingual term pairs.

This repository is the vendor-neutral public core. It does not include the original dissertation research instrument, reading and quiz system, commercial billing, hosted-service configuration, behavioral analytics, or provider-specific roster integrations.

Start with the [documentation index](docs/README.md) for the canonical reading
order covering current development state, architecture, product workflows,
authorization, generated data and route references, deployment, and the
relationship to SafeGloss Commercial.

This vNext successor is not a production deployment target. See
[VNEXT_BOOTSTRAP.md](VNEXT_BOOTSTRAP.md) for its isolated local-lab boundary.
Reviewed public direction is maintained in the
[Core roadmap](docs/product/ROADMAP.md); proposals are not commitments until
maintainers promote them explicitly.

## Core features

- Email-based teacher and student accounts
- Courses, rosters, join codes, and enrollment
- Multilingual glossaries with definitions, examples, and translations
- Per-student preferred-language display
- Manual and scheduled Study/Exam Mode
- Exam approval at the term level
- UTF-8 CSV import and formula-safe CSV export
- Print-friendly glossary views
- No AI, analytics, payment, or identity-provider account required

## Quick start with Docker

Requirements: Docker Engine with Docker Compose.

```bash
docker compose up --build
```

Open <http://localhost:8000>, create a teacher account, and begin with a course or glossary. PostgreSQL data is stored in the `postgres-data` Docker volume.

To create an administrator:

```bash
docker compose exec web python manage.py createsuperuser
```

## Local development

SafeGloss supports Python 3.12+ and PostgreSQL. PostgreSQL is the canonical database for development, CI, and deployment.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
cp .env.example .env
python manage.py migrate
python manage.py seed_languages
python manage.py createsuperuser
python manage.py runserver
```

Run the quality gates:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
pytest
ruff check .
ruff format --check .
pip-audit -r requirements.txt
python scripts/generate_documentation.py --check
python scripts/check_documentation_links.py
python scripts/check_documentation_updates.py
```

## Install from a built artifact

Core is not yet published to a package index. A reviewed source distribution
or wheel can nevertheless be installed into a self-hosted Python environment:

```bash
python -m pip install safegloss_core-0.1.0-py3-none-any.whl
export DJANGO_SECRET_KEY="replace-with-a-long-random-secret"
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:5432/safegloss"
export ALLOWED_HOSTS="glossary.example.edu"
export STATIC_ROOT="/srv/safegloss/staticfiles"
safegloss-core migrate --noinput
safegloss-core seed_languages
safegloss-core collectstatic --noinput
```

Use `safegloss-core` in place of `python manage.py` after installation. Build
artifacts locally with `python -m build`; CI installs both the wheel and source
distribution into clean environments and smoke-tests them against PostgreSQL.
Artifact publication, version tags, and Hosted dependency pinning are separate
reviewed work.

## CSV format

The only required column is `phrase`. Supported optional columns are:

```text
phrase,translation,language_code,definition,example,part_of_speech,is_exam_approved
```

Language codes must already exist in the language catalog. Run `python manage.py seed_languages` to install the small built-in catalog.

## Exam Mode scope

Exam Mode restricts what SafeGloss renders. It is not a locked browser, proctoring system, or guarantee that a student cannot reach information outside SafeGloss. Read [the security model](docs/development/SECURITY_MODEL.md) before using it in an assessment.

## Project structure

```text
accounts/   email authentication, roles, language preference
core/       languages, subjects, landing page, dashboard
courses/    courses, rosters, enrollment, glossary links, mode scheduling
glossary/   glossaries, terms, translations, import/export, student views
config/     vendor-neutral Django configuration and package-owned assets
safegloss_core/ public distribution and command-line entry point
```

The architectural boundary and exclusions are recorded in [ADR-0001](docs/decisions/0001-public-core-boundary.md).
The current runtime structure, data flows, domain ownership, and extension
rules are documented in the [system architecture](docs/architecture/SYSTEM.md).

## Relationship to safegloss.com

The service at `safegloss.com` is a private downstream distribution of SafeGloss Core.
It combines this public foundation with hosted-only integrations, operations, research,
and branding. Core remains independently self-hostable and does not require access to
the hosted repository or any hosted provider account.

Accepted Core changes are periodically merged downstream through reviewed integration
branches. Hosted-only code is not automatically copied back into Core.

## Privacy and outbound services

The default application does not load analytics, call an AI provider, send email, or connect to a school information system. Console email is used by default. Operators are responsible for their deployment, backups, access policy, and applicable student-data requirements.

Never commit `.env`, database exports, media uploads, access tokens, or production configuration. See [SECURITY.md](SECURITY.md).

## Contributing

Bug reports and pull requests are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md) and the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

SafeGloss Core source code is available under the [MIT License](LICENSE). The license does not grant trademark rights; see [TRADEMARKS.md](TRADEMARKS.md).
