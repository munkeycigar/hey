# Hey Localhost Docker Compose Deployment Implementation Plan

> **For executing agents:** Apply the `subagent-driven-development` skill (recommended) or `executing-plans` skill to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `docker compose up -d --build` deploy Hey locally on `127.0.0.1:9600` with a bundled PostgreSQL service for the existing Cloudflare Tunnel to target.

**Architecture:** Build a production-style Django image that runs migrations, collects static files, and starts Gunicorn. Compose will run two services, `app` and `db`, with Postgres data stored in a named volume and only the Django app published to the host loopback interface.

**Tech Stack:** Django 5.2, Gunicorn, WhiteNoise, PostgreSQL 16 Alpine, Docker Compose.

**Relevant Alfreds agents:** coding owns file edits and local smoke testing; testing owns verification commands; code_review should confirm no secrets are committed and no API surface changed.

---

## File Structure

- Create `Dockerfile` — builds the Django app image from `python:3.12-slim`.
- Create `.dockerignore` — keeps secrets, git metadata, virtualenvs, and generated files out of the Docker build context.
- Create `docker/entrypoint.sh` — runs `migrate`, `collectstatic`, then `gunicorn config.wsgi:application`.
- Modify `docker-compose.yml` — replaces the current dev-style app-only compose with `app` and `db` services, `127.0.0.1:9600:8000`, deployment env, healthchecks, and a named Postgres volume.
- Modify `.env.example` — documents local Python development values and Docker deployment values that match Compose.
- Modify `README.md` — adds deployment commands and Cloudflare Tunnel origin guidance.
- Create `docs/README.md` — human-facing project documentation index.
- Create `docs/architecture.md` — human-facing architecture summary including the Compose deployment shape.
- Create `docs/features/deployment.md` — user-facing deployment feature guide.
- Create `docs/CHANGELOG.md` — notable user-visible changes, newest first.
- Modify `ARCHITECTURE.md` — updates canonical project architecture with the Docker Compose deployment layer.

---

### Task 1: Add Docker App Image

**Files:**
- Create: `Dockerfile`
- Create: `.dockerignore`
- Create: `docker/entrypoint.sh`

**Assigned agent:** coding

- [ ] **Step 1: Verify the current failure**

Run via `run_command`:

```bash
docker compose build app
```

Expected: FAIL with `failed to read dockerfile: open Dockerfile: no such file or directory`.

- [ ] **Step 2: Create `.dockerignore`**

Write this exact file:

```dockerignore
.git
.gitignore
.env
.env.*
!.env.example
__pycache__/
*.py[cod]
*.egg-info/
.eggs/
venv/
.venv/
env/
db.sqlite3
db.sqlite3-journal
staticfiles/
media/
.DS_Store
Thumbs.db
.idea/
.vscode/
.worktrees/
.attachments/
.alfreds-*.pid
```

- [ ] **Step 3: Create `Dockerfile`**

Write this exact file:

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

COPY . .
RUN chmod +x /app/docker/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/docker/entrypoint.sh"]
```

- [ ] **Step 4: Create `docker/entrypoint.sh`**

Create the `docker/` directory, then write this exact file:

```sh
#!/bin/sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${WEB_CONCURRENCY:-2}" \
  --timeout "${WEB_TIMEOUT:-60}"
```

- [ ] **Step 5: Build the app image**

Run via `run_command`:

```bash
docker build -t hey-app:test .
```

Expected: PASS and finish with a successfully built `hey-app:test` image.

- [ ] **Step 6: Commit**

```bash
git add Dockerfile .dockerignore docker/entrypoint.sh
git commit -m "chore: add docker app image"
```

---

### Task 2: Replace Compose With App + Postgres Deployment

**Files:**
- Modify: `docker-compose.yml`
- Modify: `.env.example`

**Assigned agent:** coding

- [ ] **Step 1: Confirm the current Compose shape**

Run via `run_command`:

```bash
docker compose config --services
```

Expected before editing: only `app` is listed.

- [ ] **Step 2: Replace `docker-compose.yml`**

Write this exact file:

```yaml
name: hey

services:
  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-hey}
      POSTGRES_USER: ${POSTGRES_USER:-hey}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-hey-local-change-me}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-hey} -d ${POSTGRES_DB:-hey}"]
      interval: 5s
      timeout: 5s
      retries: 10
    volumes:
      - postgres_data:/var/lib/postgresql/data

  app:
    build:
      context: .
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    ports:
      - "127.0.0.1:9600:8000"
    environment:
      PORT: "8000"
      WEB_CONCURRENCY: ${WEB_CONCURRENCY:-2}
      WEB_TIMEOUT: ${WEB_TIMEOUT:-60}
      SECRET_KEY: ${SECRET_KEY:-dev-insecure-key-change-me-before-deploying-anywhere}
      DEBUG: ${DEBUG:-False}
      ALLOWED_HOSTS: ${ALLOWED_HOSTS:-hey.leorey.es,localhost,127.0.0.1}
      CSRF_TRUSTED_ORIGINS: ${CSRF_TRUSTED_ORIGINS:-https://hey.leorey.es,http://localhost:9600,http://127.0.0.1:9600}
      DATABASE_URL: ${DATABASE_URL:-postgres://hey:hey-local-change-me@db:5432/hey}
      TIME_ZONE: ${TIME_ZONE:-UTC}
      SECURE_SSL_REDIRECT: ${SECURE_SSL_REDIRECT:-False}

volumes:
  postgres_data:
```

- [ ] **Step 3: Replace `.env.example`**

Write this exact file:

```dotenv
# Copy this file to .env and adjust values before running the app.

# Generate one with:
#   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
SECRET_KEY=change-me-to-a-long-random-string

# Local Python development defaults.
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=
DATABASE_URL=postgres://postgres:postgres@localhost:5432/hey
TIME_ZONE=UTC

# Docker Compose deployment defaults for hey.leorey.es via Cloudflare Tunnel.
# The tunnel should target http://127.0.0.1:9600 on the Docker host.
POSTGRES_DB=hey
POSTGRES_USER=hey
POSTGRES_PASSWORD=change-me-to-a-long-random-string
WEB_CONCURRENCY=2
WEB_TIMEOUT=60
SECURE_SSL_REDIRECT=False

# For Docker deployment, set these values in .env:
# DEBUG=False
# ALLOWED_HOSTS=hey.leorey.es,localhost,127.0.0.1
# CSRF_TRUSTED_ORIGINS=https://hey.leorey.es,http://localhost:9600,http://127.0.0.1:9600
# DATABASE_URL=postgres://hey:change-me-to-a-long-random-string@db:5432/hey
```

- [ ] **Step 4: Validate Compose configuration**

Run via `run_command`:

```bash
docker compose config --services
```

Expected: output includes exactly these service names:

```text
db
app
```

Run via `run_command`:

```bash
docker compose config
```

Expected: rendered config includes `127.0.0.1:9600`, `postgres_data`, `hey.leorey.es`, and `CSRF_TRUSTED_ORIGINS`.

- [ ] **Step 5: Commit**

```bash
git add docker-compose.yml .env.example
git commit -m "chore: add localhost compose deployment"
```

---

### Task 3: Document Deployment And Architecture

**Files:**
- Modify: `README.md`
- Create: `docs/README.md`
- Create: `docs/architecture.md`
- Create: `docs/features/deployment.md`
- Create: `docs/CHANGELOG.md`
- Modify: `ARCHITECTURE.md`

**Assigned agent:** coding

- [ ] **Step 1: Add this section to `README.md` after the local setup section**

```markdown
---

## Docker Compose deployment on localhost:9600

This repository includes a local production-style Docker Compose deployment for
the host that already runs Cloudflare Tunnel. Compose starts the Django app and a
PostgreSQL database. It does not configure Cloudflare, DNS, TLS certificates, or
the tunnel service.

### 1. Configure deployment environment

```bash
cp .env.example .env
```

Edit `.env` and set:

```dotenv
SECRET_KEY=<generate-a-real-django-secret-key>
DEBUG=False
ALLOWED_HOSTS=hey.leorey.es,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://hey.leorey.es,http://localhost:9600,http://127.0.0.1:9600
POSTGRES_DB=hey
POSTGRES_USER=hey
POSTGRES_PASSWORD=<use-a-long-random-password>
DATABASE_URL=postgres://hey:<same-password-url-encoded-if-needed>@db:5432/hey
```

Generate a Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 2. Start the stack

```bash
docker compose up -d --build
docker compose ps
```

The app listens only on the Docker host loopback interface:

```text
http://127.0.0.1:9600
```

Point the existing Cloudflare Tunnel origin for `hey.leorey.es` to:

```text
http://127.0.0.1:9600
```

### 3. Verify the deployment

```bash
curl -I http://127.0.0.1:9600/accounts/login/
curl -I -H "Host: hey.leorey.es" -H "X-Forwarded-Proto: https" http://127.0.0.1:9600/accounts/login/
docker compose logs -f app
```

Expected: the login route returns `HTTP/1.1 200 OK`.

### 4. Admin and maintenance commands

Create an admin user:

```bash
docker compose exec app python manage.py createsuperuser
```

Run migrations manually:

```bash
docker compose exec app python manage.py migrate
```

View logs:

```bash
docker compose logs -f app
docker compose logs -f db
```

Update after pulling changes:

```bash
git pull
docker compose up -d --build
docker compose logs -f app
```

Stop the stack without deleting database data:

```bash
docker compose down
```

Delete the local database volume:

```bash
docker compose down -v
```
```

- [ ] **Step 2: Create `docs/README.md`**

Write this exact file:

```markdown
# Hey Documentation

Hey is a Django app for creating virtual business cards with QR codes and vCard downloads.

## Audience

These docs are for maintainers who run, deploy, and extend the project.

## How to run

- Local Python development: follow `README.md`.
- Local Docker deployment: follow `docs/features/deployment.md`.

## Tech stack

- Django 5.2
- PostgreSQL
- Gunicorn
- WhiteNoise
- Docker Compose

## Documentation map

- `docs/architecture.md` — high-level system shape and data flow.
- `docs/features/deployment.md` — localhost Docker Compose deployment.
- `docs/CHANGELOG.md` — notable user-visible changes.
```

- [ ] **Step 3: Create `docs/architecture.md`**

Write this exact file:

```markdown
# Hey Architecture

Hey is a Django 5.2 app that stores virtual business cards in PostgreSQL. Users authenticate with Django's session auth, create cards, and download QR PNG or vCard files from server-rendered routes.

## Runtime shape

- `config/` contains Django settings, URL routing, WSGI, and ASGI entrypoints.
- `accounts/` contains registration and login/logout views.
- `cards/` contains the business card model, forms, views, templates, QR output, and vCard output.
- `static/` contains shared CSS served by WhiteNoise in Docker.
- `docker-compose.yml` runs the app and database for localhost deployment.

## Deployment flow

Docker Compose builds the Django image from `Dockerfile`, starts PostgreSQL, waits for database health, then starts the app through `docker/entrypoint.sh`.

The app startup flow is:

1. `python manage.py migrate --noinput`
2. `python manage.py collectstatic --noinput`
3. `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

Compose publishes the app on `127.0.0.1:9600`. Cloudflare Tunnel is managed outside this repository and should target `http://127.0.0.1:9600`.

## Data flow

Browser requests reach Django through either local development or the Cloudflare Tunnel origin. Authenticated users manage `cards.BusinessCard` records. QR PNG and `.vcf` responses are generated from card data at request time.
```

- [ ] **Step 4: Create `docs/features/deployment.md`**

Write this exact file:

```markdown
# Localhost Docker Compose Deployment

The Docker Compose deployment runs Hey on a local server at `127.0.0.1:9600` with a PostgreSQL container. It is intended for a machine where Cloudflare Tunnel is already installed and configured separately.

## What it does

- Builds a Django app image.
- Starts PostgreSQL with a persistent named volume.
- Runs migrations and static file collection on app startup.
- Serves the app through Gunicorn.
- Binds the app to `127.0.0.1:9600` on the host.

## What it does not do

- It does not create or configure Cloudflare Tunnel.
- It does not manage DNS.
- It does not terminate TLS inside Docker.

## Commands

Start:

```bash
docker compose up -d --build
```

Check status:

```bash
docker compose ps
```

Check the local app:

```bash
curl -I http://127.0.0.1:9600/accounts/login/
```

Follow app logs:

```bash
docker compose logs -f app
```

Stop without deleting data:

```bash
docker compose down
```

## Cloudflare Tunnel origin

Configure the existing tunnel to send `hey.leorey.es` to:

```text
http://127.0.0.1:9600
```
```

- [ ] **Step 5: Create `docs/CHANGELOG.md`**

Write this exact file:

```markdown
# Changelog

## 2026-06-05

- Added a local Docker Compose deployment design for serving Hey on `127.0.0.1:9600` behind an existing Cloudflare Tunnel.
```

- [ ] **Step 6: Replace `ARCHITECTURE.md`**

Write this exact file:

```markdown
# Architecture — Hey

_Canonical architectural map for this project. Both human developers and AI agents should read this before making structural changes. Keep it current as the system evolves._

## Product Shape

Hey is a virtual business card app. Authenticated users create contact cards, view them in the browser, download `.vcf` contact files, and access QR PNGs for adding contacts from phones.

## Tech Stack

- Django 5.2 — web framework, session auth, templates, ORM, admin.
- PostgreSQL — persistent database for users and business cards.
- Gunicorn — production WSGI server in Docker.
- WhiteNoise — static file serving for collected assets.
- Docker Compose — local deployment with `app` and `db` services.

## Key Directories

- `config/` — Django settings, URL routing, WSGI, and ASGI entrypoints.
- `accounts/` — registration and login/logout flows.
- `cards/` — business card model, forms, views, templates, QR PNG output, and vCard output.
- `static/` — shared CSS.
- `docker/` — container startup scripts.
- `docs/` — human-facing project documentation.
- `implementation-plans/` — Alfreds implementation plans.
- `CLAUDE.md` / `AGENTS.md` — agent context and conventions.

## Data Model

- `cards.BusinessCard` belongs to a Django auth user through `owner`.
- Card fields store contact identity, organization, phone, email, website, and timestamps.
- `BusinessCard.to_vcard()` serializes a card to vCard 3.0 text for QR and `.vcf` responses.

## Request / Execution Flow

Browser requests enter Django through `config.urls`. Account routes handle registration and auth. Card routes enforce owner isolation, render templates, and generate QR PNG or `.vcf` responses from card records.

For Docker deployment, Compose starts PostgreSQL first, waits for database health, then starts the Django app. The app entrypoint runs migrations, collects static files, and launches Gunicorn on container port `8000`. Compose publishes that port on `127.0.0.1:9600` only.

## Auth & Permissions

Django session auth protects card management. Card views filter by the logged-in user so one user cannot view, edit, delete, or download another user's card.

## Deployment

The local deployment target is a Docker host with Cloudflare Tunnel already running outside this repository. `docker-compose.yml` runs:

- `db` — PostgreSQL with a named `postgres_data` volume.
- `app` — Django/Gunicorn image built from the repository.

The public host `hey.leorey.es` should point through the existing tunnel to `http://127.0.0.1:9600`.

## Important Conventions

- Read configuration from environment variables.
- Keep secrets out of source files and `.env.example`.
- Use trailing slashes in Django routes.
- Do not add Cloudflare Tunnel service management to this repository.
- Read `API.md` before changing endpoints, payloads, auth behavior, errors, or webhooks.

## Known Tradeoffs

- The Compose deployment runs migrations automatically on app startup for operational simplicity.
- TLS termination is delegated to Cloudflare Tunnel.
- The app binds to host loopback only, which is correct for a local tunnel origin and avoids exposing port `9600` on the LAN.

## Open Questions

- None.
```

- [ ] **Step 7: Commit**

```bash
git add README.md docs/README.md docs/architecture.md docs/features/deployment.md docs/CHANGELOG.md ARCHITECTURE.md
git commit -m "docs: document localhost compose deployment"
```

---

### Task 4: Smoke Test Local Deployment

**Files:**
- Verify: `Dockerfile`
- Verify: `docker-compose.yml`
- Verify: `docker/entrypoint.sh`
- Verify: `README.md`
- Verify: `docs/features/deployment.md`

**Assigned agent:** testing

- [ ] **Step 1: Run Django unit tests before container testing**

Run via `run_command`:

```bash
python manage.py test
```

Expected: PASS for the existing `cards` tests.

- [ ] **Step 2: Build and start the Compose stack**

Run via `run_command`:

```bash
docker compose up -d --build
```

Expected: PASS. The `db` service becomes healthy and the `app` service starts.

- [ ] **Step 3: Confirm both services are running**

Run via `run_command`:

```bash
docker compose ps
```

Expected: `db` is healthy/running and `app` is running with `127.0.0.1:9600->8000/tcp`.

- [ ] **Step 4: Confirm the local login page responds**

Run via `run_command`:

```bash
curl -I http://127.0.0.1:9600/accounts/login/
```

Expected: `HTTP/1.1 200 OK`.

- [ ] **Step 5: Confirm the public host header works through the local origin**

Run via `run_command`:

```bash
curl -I -H "Host: hey.leorey.es" -H "X-Forwarded-Proto: https" http://127.0.0.1:9600/accounts/login/
```

Expected: `HTTP/1.1 200 OK`.

- [ ] **Step 6: Confirm Django checks pass inside the app container**

Run via `run_command`:

```bash
docker compose exec app python manage.py check
```

Expected: `System check identified no issues`.

- [ ] **Step 7: Inspect app logs**

Run via `run_command`:

```bash
docker compose logs app
```

Expected: logs show migrations completed, static files collected, and Gunicorn listening on `0.0.0.0:8000`.

- [ ] **Step 8: Commit any smoke-test fixes**

If smoke testing required a file fix, commit only the touched files:

```bash
git status --short
git add <fixed-file-paths>
git commit -m "fix: complete compose deployment smoke test"
```

If no files changed, do not create an empty commit.

---

## Self-Review

- Spec coverage: the plan covers Dockerfile, entrypoint, app + Postgres Compose, loopback port `9600`, deployment environment, Cloudflare origin docs, architecture docs, and smoke tests.
- Placeholder scan: no incomplete implementation steps remain. Example secrets are named as values the deployer must replace in `.env`.
- Type and command consistency: service names are `app` and `db` throughout; Django entrypoint is `config.wsgi:application`; published host port is `127.0.0.1:9600`; Postgres defaults are `hey` / `hey` / `hey-local-change-me`.
