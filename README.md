# mitre-technique-service

Django/DRF microservice that serves the MITRE ATT&CK Enterprise matrix for the CyberRangeCZ
Platform. It retrieves tactics and techniques from MITRE's TAXII 2.1 server, caches them in redis,
and renders an HTML matrix in which each cell is marked with the training definitions that exercise
that technique.

## Data sources

| Source | Purpose | Failure behaviour |
| --- | --- | --- |
| MITRE TAXII 2.1 collection (`attack-taxii.mitre.org`, Enterprise ATT&CK) | Tactics, techniques, technique index | Falls back to the pickled `mitre_attack_backup_data` file |
| redis | Holds the parsed matrix indefinitely; refreshed only on explicit request | Cold cache is filled from the pickled backup file |
| Training service | MITRE techniques per training definition, flagged as played by the requesting user | Propagated as an error response |

Techniques are keyed as `TACTIC.TECHNIQUE` (for example `TA0043.T1595`). A sub-technique's third
segment is folded into its parent, so `TA0043.T1595.001` and `TA0043.T1595` occupy the same cell.

## API

All routes are prefixed with `<microservice_name>/api/v1/`, by default
`mitre-technique-service/api/v1/`.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `mitre-matrix-visualisation?played=<bool>` | HTML matrix of tactics and techniques annotated with training definitions. `played=true` restricts it to definitions the caller has played; any other value includes the whole catalogue. Requires an `Authorization` header, which is forwarded to the training service. |
| `GET` | `mitre-technique-index` | `{"techniques": [{"code", "name"}]}` for every technique in the matrix. |
| `GET` | `mitre-technqiue-index` | Misspelled legacy alias of the above. |
| `PUT` | `mitre-update-matrix-data` | Refreshes the cached matrix from the TAXII server, falling back to the pickled backup. Returns `{"message"}` stating which source was used. |
| `GET` | `schema/` | OpenAPI schema (drf-spectacular). |
| `GET` | `doc/` | Swagger UI. |

Errors are rendered by `crczp.mitre_common_lib.exc_handler` as `{"detail": "<message>"}`, with `400`
for this project's own exceptions and `500` for anything unhandled.

## Configuration

`DJANGO_SECRET_KEY` must be present in the environment; the service refuses to start without it. Any
high-entropy string will do, as nothing durable is signed.

Everything else comes from `config.yml`, parsed by yamlize, which **rejects unknown keys** — a stale
or misspelled key stops the service at startup rather than being ignored.

| Key | Default | Meaning |
| --- | --- | --- |
| `microservice_name` | `mitre-technique-service` | First segment of every route |
| `debug` | `True` | Django `DEBUG`; turn off in production |
| `allowed_hosts` | `['*']` | Django `ALLOWED_HOSTS` |
| `cors_origin_allow_all` | `True` | Accept any origin |
| `cors_origin_whitelist` | `[]` | Accepted origins when the above is off |
| `application_configuration.ssl_ca_certificate_verify` | `/etc/ssl/certs` | CA bundle for calls to related services |
| `application_configuration.training_mitre_techniques_endpoint` | `http://127.0.0.1:8083/training/api/v1/training-definitions/played-mitre-techniques` | Training service endpoint supplying per-definition MITRE techniques |
| `application_configuration.file_storage_location` | `crczp/mitre_matrix_visualizer_app/templates/` | Directory holding the Jinja2 template and the pickled MITRE backup |
| `application_configuration.redis.{host,port,db}` | `localhost`, `6379`, `1` | Cache connection |

## Local development

```bash
uv sync
DJANGO_SECRET_KEY=$(head -c 32 /dev/urandom | base64) uv run python manage.py runserver 8001
```

A reachable redis is required; on a cold cache the matrix is loaded from the pickled backup file.

## Quality gate

```bash
uv run tox            # pre-commit (ruff lint, ruff format, mypy), pylint, bandit, audit, pytest
uv run tox -e pytest  # tests plus manage.py check
```

`pytest` runs against `crczp.mitre_technique_project.tests.settings`, which carries its own
throwaway secret key, so no environment variable is needed for tests.
