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
