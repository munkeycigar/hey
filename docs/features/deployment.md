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

## Configure

Copy the environment template and set deployment secrets before starting the stack:

```bash
cp .env.example .env
```

Set `DEBUG=False`, generate a real `SECRET_KEY`, choose a long random `POSTGRES_PASSWORD`, and make `DATABASE_URL` use the same password with the Compose service hostname:

```dotenv
DATABASE_URL=postgres://hey:<same-password-url-encoded-if-needed>@db:5432/hey
```

## Start

```bash
docker compose up -d --build
docker compose ps
```

## Verify

Check the local app origin:

```bash
curl -I http://127.0.0.1:9600/accounts/login/
```

Check the public host header through the local origin:

```bash
curl -I -H "Host: hey.leorey.es" -H "X-Forwarded-Proto: https" http://127.0.0.1:9600/accounts/login/
```

Expected: the login route returns `HTTP/1.1 200 OK`.

## Logs

Follow app logs:

```bash
docker compose logs -f app
```

Follow database logs:

```bash
docker compose logs -f db
```

## Update

After pulling repository changes, rebuild and restart the stack:

```bash
git pull
docker compose up -d --build
docker compose logs -f app
```

## Stop

Stop without deleting database data:

```bash
docker compose down
```

Delete the local database volume:

```bash
docker compose down -v
```

## Cloudflare Tunnel origin

Configure the existing tunnel to send `hey.leorey.es` to:

```text
http://127.0.0.1:9600
```
