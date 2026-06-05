# Architecture — Hey

_Canonical architectural map for this project. Both human developers and AI agents should read this before making structural changes. Keep it current as the system evolves._

## Product Shape
virtual business card

## Tech Stack
- Django 5.2 backend
- PostgreSQL database configured through `DATABASE_URL`
- WhiteNoise static file serving
- Gunicorn application server
- Docker app image built from `python:3.12-slim`
- Docker Compose local deployment with `app` and PostgreSQL `db` services

## Key Directories
- `docs/` — human-facing project documentation
- `docker/` — container startup scripts
- `Dockerfile` — production-style Django app image build
- `docker-compose.yml` — localhost deployment stack for `app` and `db`
- `.dockerignore` — Docker build context exclusions for secrets and generated files
- `CLAUDE.md` / `AGENTS.md` — agent context and conventions

## Data Model
<!-- Describe the main entities, relationships, and persistence strategy. -->

## Request / Execution Flow
In the Docker app image, `docker/entrypoint.sh` runs database migrations, collects static files, and then starts `gunicorn config.wsgi:application` on `0.0.0.0:${PORT:-8000}`.

For local deployment, Docker Compose starts PostgreSQL 16 Alpine as `db`, waits for its `pg_isready` healthcheck, then starts the Django `app`. Compose publishes the app on `127.0.0.1:9600:8000` and stores database files in the named `postgres_data` volume.

## Auth & Permissions
<!-- Describe authentication, authorization, roles, and where permission checks happen. -->

## Agent Orchestration
<!-- Describe the AI agents involved, their responsibilities, handoff points, and files they should read before making changes. -->

All agents must read this `ARCHITECTURE.md` and `CLAUDE.md` before making structural changes.

## Important Conventions
- Keep secrets and generated runtime files out of Docker build contexts with `.dockerignore`.
- Container startup should go through `docker/entrypoint.sh` so migrations and static collection run before Gunicorn.
- Compose should bind the app to host loopback only (`127.0.0.1:9600`) so an external Cloudflare Tunnel can target that local origin without exposing the container directly on all interfaces.

## Known Tradeoffs
<!-- Record intentional shortcuts, constraints, or decisions that future agents should not accidentally undo. -->

## Open Questions
<!-- Track unresolved architectural decisions. -->
