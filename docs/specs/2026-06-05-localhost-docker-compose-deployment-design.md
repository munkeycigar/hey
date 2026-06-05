# Project: Hey Localhost Docker Compose Deployment

## Overview
Hey is a Django 5 virtual business card app. This design adds a deployment path for running the app and its PostgreSQL database with Docker Compose on the same host where Cloudflare Tunnel is already running. The app will listen on `127.0.0.1:9600`, and the existing tunnel will point `hey.leorey.es` at that local origin.

This design intentionally does not configure Cloudflare Tunnel, TLS certificates, DNS, or a reverse proxy, because those responsibilities are already handled outside this repository.

## Requirements
- Provide a Docker Compose deployment that includes both the Django app and PostgreSQL.
- Expose the Django app only on localhost at `127.0.0.1:9600`.
- Run Django behind Gunicorn inside the app container.
- Preserve database data across container restarts with a named Docker volume.
- Configure Django for `hey.leorey.es`, `localhost`, and `127.0.0.1` hostnames.
- Configure CSRF trusted origins for `https://hey.leorey.es`, `http://localhost:9600`, and `http://127.0.0.1:9600`.
- Run migrations and collect static files during container startup.
- Keep Cloudflare Tunnel setup out of the repository.
- Document the deployment commands and required environment variables for maintainers.

## Technical Stack
- Backend: Django 5.2
- Application server: Gunicorn
- Static files: WhiteNoise with compressed static file storage
- Database: PostgreSQL in Docker Compose
- Deployment target: local Docker host bound to `127.0.0.1:9600`
- Public ingress: existing Cloudflare Tunnel mapping `hey.leorey.es` to the local app

## Architecture
The deployment consists of two Compose services:

- `app`: builds the Django project image from the repository, waits for PostgreSQL readiness through normal startup ordering, runs `python manage.py migrate`, runs `python manage.py collectstatic --noinput`, then starts `gunicorn config.wsgi:application --bind 0.0.0.0:8000`.
- `db`: runs PostgreSQL with a named volume for `/var/lib/postgresql/data`.

The host publishes only the Django container port:

```text
127.0.0.1:9600 -> app:8000
```

Cloudflare Tunnel remains an external dependency. The tunnel should target `http://127.0.0.1:9600`, which lets Cloudflare terminate HTTPS publicly while Django sees forwarded HTTPS headers through the tunnel.

## Features
### Feature 1: Localhost Compose Runtime
- Description: Run the complete Hey app stack with Docker Compose on a local server.
- Acceptance Criteria:
  - [ ] `docker compose up -d --build` starts `app` and `db`.
  - [ ] `curl http://127.0.0.1:9600/` receives a Django response.
  - [ ] The `app` service runs Gunicorn, not `manage.py runserver`.
  - [ ] The `db` service stores data in a named volume.
  - [ ] The Compose file does not include or manage Cloudflare Tunnel.

### Feature 2: Deployment Environment Configuration
- Description: Provide safe defaults for local production-style deployment behind Cloudflare.
- Acceptance Criteria:
  - [ ] `DEBUG=False` is used for the Compose deployment.
  - [ ] `ALLOWED_HOSTS` includes `hey.leorey.es`, `localhost`, and `127.0.0.1`.
  - [ ] `CSRF_TRUSTED_ORIGINS` includes `https://hey.leorey.es`, `http://localhost:9600`, and `http://127.0.0.1:9600`.
  - [ ] `DATABASE_URL` points from the app container to the Compose database service.
  - [ ] `SECRET_KEY` is configurable without baking secrets into source.

### Feature 3: Deployment Documentation
- Description: Document how a maintainer deploys, checks, and updates the local Compose stack.
- Acceptance Criteria:
  - [ ] README or human-facing docs include build, start, stop, logs, migration, and admin user commands.
  - [ ] Documentation states that Cloudflare Tunnel is managed outside this repo.
  - [ ] Documentation states the expected tunnel origin is `http://127.0.0.1:9600`.
  - [ ] Documentation explains which environment values must be changed for real deployment.

## Integration Map
| Feature | Reads from | Writes to / Affects |
|---------|------------|---------------------|
| Localhost Compose Runtime | Django settings, `requirements.txt`, app code, PostgreSQL image configuration | Starts the app and database containers; persists application data in the Postgres volume |
| Deployment Environment Configuration | Django environment variables consumed by `config/settings.py` | Affects request host validation, CSRF validation, database connection behavior, secure cookie behavior, and static file collection |
| Deployment Documentation | Compose runtime behavior and Django environment configuration | Helps future maintainers run and troubleshoot the deployment without modifying Cloudflare Tunnel config |

## Implementation Tasks
1. [ ] Add a production-style Dockerfile for the Django app (estimated complexity: medium).
2. [ ] Add an entrypoint script that runs migrations, collects static files, and starts Gunicorn (estimated complexity: medium).
3. [ ] Update `docker-compose.yml` to define `app` and `db`, bind `127.0.0.1:9600:8000`, set deployment environment values, and use a named Postgres volume (estimated complexity: medium).
4. [ ] Update `.env.example` and human-facing docs with deployment variables and commands (estimated complexity: low).
5. [ ] Smoke-test the Compose deployment locally with `docker compose up -d --build`, `docker compose ps`, `docker compose logs`, and `curl http://127.0.0.1:9600/` (estimated complexity: medium).

## Questions/Clarifications Needed
- The implementation plan should use non-secret example defaults for Compose, but the deployed system must use a real `SECRET_KEY` and database password before public use.
- The Cloudflare Tunnel origin is assumed to be `http://127.0.0.1:9600`; if the existing tunnel uses a different local origin, the Compose host port should stay aligned with the tunnel configuration.

## Out of Scope
- Creating or modifying Cloudflare Tunnel config.
- Managing DNS records.
- Adding TLS termination inside Docker.
- Changing API endpoints, payloads, auth flows, webhooks, or public card behavior.
