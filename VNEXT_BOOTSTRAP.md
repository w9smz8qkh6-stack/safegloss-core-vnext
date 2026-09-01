# SafeGloss Core vNext bootstrap

This repository is a public, non-production successor candidate seeded at
`0482706302a82a87eedc87b681038d9f08a393a1` and tagged
`legacy-baseline-2026-09-01`. It must never receive Hosted code, credentials,
provider configuration, production data, or commercial operational records.

## Local lab

The vNext lab is intentionally isolated from the current production deployment:

```bash
cp .env.vnext-lab.example .env.vnext-lab
# Replace both placeholder secrets with locally generated values.
docker compose --env-file .env.vnext-lab -f compose.vnext-lab.yaml config
docker compose --env-file .env.vnext-lab -f compose.vnext-lab.yaml up --build
```

It creates only the named `safegloss-core-vnext-lab-postgres-data` volume and
binds the web service to `127.0.0.1` by default. Do not change the project
name, use external volumes, attach the production network, or expose an ingress
route. This first lab may use only empty or synthetic data.

No package release is authorized by this bootstrap. Releases require the later
protected-tag, reproducible-build, SBOM/provenance, PyPI Trusted Publishing, and
clean-install acceptance controls recorded in the private SafeGloss portfolio.
