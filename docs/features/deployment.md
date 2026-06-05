# Docker App Image

## What It Does
The project includes a Docker build path for the Django app. The image installs the app dependencies, copies the source into `/app`, and starts with an entrypoint that prepares the database/static assets before launching Gunicorn.

## Build
```bash
docker build -t hey-app:test .
```

## Runtime Behavior
`docker/entrypoint.sh` runs migrations, collects static files, and then starts:

```bash
gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
```

Set `PORT`, `WEB_CONCURRENCY`, and `WEB_TIMEOUT` to tune the container process. The app also requires the usual Django environment values such as `SECRET_KEY`, `DATABASE_URL`, `ALLOWED_HOSTS`, and `CSRF_TRUSTED_ORIGINS`.

## Build Context Safety
`.dockerignore` excludes local secrets, git metadata, virtualenvs, SQLite files, collected static files, media uploads, editor files, and Alfreds internal workspace files from the image build context.

## Current Scope
This task adds the app image only. Replacing Compose with separate app and PostgreSQL services is covered by the next deployment task.
