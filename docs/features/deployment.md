# Docker Compose Deployment

## What It Does
The project includes a local Docker Compose deployment for the Django app and PostgreSQL. It is intended for a host where Cloudflare Tunnel is configured separately and targets the local app origin.

## Services
- `db` runs PostgreSQL 16 Alpine and stores data in the named `postgres_data` volume.
- `app` builds the Django image from the root `Dockerfile`, waits for `db` to become healthy, runs the entrypoint, and serves Gunicorn on container port `8000`.

## Configuration
Copy `.env.example` to `.env` and update secrets before starting the stack:

```bash
cp .env.example .env
```

For deployment, set `DEBUG=False`, configure `SECRET_KEY`, choose a strong `POSTGRES_PASSWORD`, and set `DATABASE_URL` to use the `db` service hostname.

## Start
```bash
docker compose up -d --build
```

The app listens on the Docker host loopback interface:

```text
http://127.0.0.1:9600
```

Point the Cloudflare Tunnel origin for `hey.leorey.es` to `http://127.0.0.1:9600`.

## Verify
```bash
docker compose config --services
docker compose config
docker compose ps
```

The rendered Compose config should include `db`, `app`, `host_ip: 127.0.0.1`, `published: "9600"`, and the `postgres_data` volume.

## Maintenance
```bash
docker compose logs -f app
docker compose logs -f db
docker compose down
docker compose down -v
```

Use `docker compose down` to stop containers while keeping database data. Use `docker compose down -v` only when the local PostgreSQL data should be deleted.
