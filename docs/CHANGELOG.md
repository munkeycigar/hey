# Changelog

## 2026-06-05 — Add Compose app and PostgreSQL deployment
- Run the local Docker deployment with `app` and `db` services.
- Bind the app to `127.0.0.1:9600` and persist PostgreSQL data in `postgres_data`.

## 2026-06-05 — Add Docker app image
- Add a Docker build path and entrypoint for the Django app container.
- Document the Docker image behavior and build context exclusions.
