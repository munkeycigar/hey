# Hey Architecture

## Product Shape
Hey is a Django virtual business card app. Users create private contact cards that can be rendered as QR codes and downloaded as vCard files.

## Runtime Components
- Django 5.2 serves the web app through `config.wsgi`.
- PostgreSQL is the configured database backend via `DATABASE_URL`.
- WhiteNoise serves collected static files.
- Gunicorn is the production-style application server.
- The Docker app image builds from `python:3.12-slim` and starts through `docker/entrypoint.sh`.
- Docker Compose runs the `app` service with a PostgreSQL `db` service for localhost deployment.

## Docker App Image
The root `Dockerfile` installs system PostgreSQL client libraries, installs `requirements.txt`, copies the app into `/app`, and exposes port `8000`.

The container entrypoint runs:

```sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Secrets and generated files are excluded from the Docker build context through `.dockerignore`.

## Docker Compose Deployment
`docker-compose.yml` defines a complete local deployment stack:

- `db` runs `postgres:16-alpine`, uses `pg_isready` for health, and persists data in the named `postgres_data` volume.
- `app` builds from the local Dockerfile, waits for `db` to become healthy, and receives deployment settings through environment variables.
- The app publishes only to host loopback at `127.0.0.1:9600:8000`.

Cloudflare Tunnel is managed outside this repository. Its origin should target `http://127.0.0.1:9600` on the Docker host.
