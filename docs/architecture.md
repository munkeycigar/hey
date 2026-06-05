# Hey Architecture

## Product Shape
Hey is a Django virtual business card app. Users create private contact cards that can be rendered as QR codes and downloaded as vCard files.

## Runtime Components
- Django 5.2 serves the web app through `config.wsgi`.
- PostgreSQL is the configured database backend via `DATABASE_URL`.
- WhiteNoise serves collected static files.
- Gunicorn is the production-style application server.
- The Docker app image builds from `python:3.12-slim` and starts through `docker/entrypoint.sh`.

## Docker App Image
The root `Dockerfile` installs system PostgreSQL client libraries, installs `requirements.txt`, copies the app into `/app`, and exposes port `8000`.

The container entrypoint runs:

```sh
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```

Secrets and generated files are excluded from the Docker build context through `.dockerignore`.
