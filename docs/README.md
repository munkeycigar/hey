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
- `docs/features/cards.md` — card viewing, QR PNG, fullscreen QR presentation, vCard downloads, and card access control.
- `docs/features/deployment.md` — localhost Docker Compose deployment.
- `docs/CHANGELOG.md` — notable user-visible changes.
