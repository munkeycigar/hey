# hey — virtual contact cards

A small Django app for creating and storing **virtual business cards**. Sign in,
save as many cards as you like (work, freelance, personal…), and each one gets a
scannable **QR code** plus a downloadable **.vcf** file. Scanning the code with a
phone camera offers a one-tap "Add Contact" — on both iOS and Android.

Built with Django 5 + PostgreSQL. Cards are encoded as standard
[vCard 3.0](https://datatracker.ietf.org/doc/html/rfc2426).

---

## Features

- Username/password auth (sign up, log in, log out)
- Each user owns many cards; cards are private to their owner
- Create / view / edit / delete cards
- Live QR preview while editing (client side)
- Permanent server-rendered QR PNG and `.vcf` download per saved card
- Django admin for managing cards

---

## Project layout

```
hey/
├── manage.py
├── requirements.txt
├── .env.example
├── config/            # project settings, urls, wsgi/asgi
├── accounts/          # registration + login/logout
├── cards/             # BusinessCard model, views, templates
├── static/css/        # shared stylesheet
└── standalone/        # the original self-contained QR generator (no backend)
```

---

## Local setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL 13+ running locally

### 2. Create the database

```bash
createdb hey
# or, from psql:
#   CREATE DATABASE hey;
```

### 3. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set a real `SECRET_KEY` and your `DATABASE_URL`. Generate a key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Migrate and run

```bash
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. You'll be sent to the login page — create an
account, then start adding cards.

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

---

## Configuration

All configuration is read from the environment (see `.env.example`):

| Variable        | Purpose                                  | Default                                          |
| --------------- | ---------------------------------------- | ------------------------------------------------ |
| `SECRET_KEY`    | Django secret key                        | insecure dev fallback (change it)                |
| `DEBUG`         | Debug mode                               | `True`                                           |
| `ALLOWED_HOSTS` | Comma-separated allowed hosts            | `localhost,127.0.0.1`                            |
| `DATABASE_URL`  | PostgreSQL connection string             | `postgres://postgres:postgres@localhost:5432/hey`|
| `TIME_ZONE`     | Server time zone                         | `UTC`                                            |

For production, set `DEBUG=False`, a strong `SECRET_KEY`, real `ALLOWED_HOSTS`,
run `python manage.py collectstatic`, and serve with `gunicorn config.wsgi`
(WhiteNoise serves the static files).

---

## Data model

`cards.BusinessCard`

| Field                         | Notes                                    |
| ----------------------------- | ---------------------------------------- |
| `owner`                       | FK to the user (cascade delete)          |
| `label`                       | Optional card name ("Work", "Freelance") |
| `first_name`, `last_name`     | Contact name                             |
| `phone`, `email`, `website`   | Contact details                          |
| `organization`, `title`       | Company / role                           |
| `created_at`, `updated_at`    | Timestamps                               |

`BusinessCard.to_vcard()` returns the vCard 3.0 string used for the QR and `.vcf`.

---

## Pushing to GitHub

This repository is already initialised with a first commit and the remote
`origin` set to `git@github.com:munkeycigar/hey.git`. From your own machine
(where your GitHub SSH key lives):

```bash
git push -u origin main
```

If the remote already has commits (for example a README created on GitHub), you
may need to reconcile first:

```bash
git pull --rebase origin main
git push -u origin main
```
