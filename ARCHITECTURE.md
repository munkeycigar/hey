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
