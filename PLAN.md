# Plan — Add Docker App Image

## Goal
Add the Docker build path for the Django app so Compose can build a production-style app image.

## Checklist
- [x] Verify the current Docker app build failure before implementation.
- [x] Create `.dockerignore` to keep secrets, git metadata, virtualenvs, and generated files out of the build context.
- [x] Create `Dockerfile` for the Django app image.
- [x] Create `docker/entrypoint.sh` to run migrations, collectstatic, and Gunicorn.
- [x] Update human-facing docs for the Docker app image.
- [ ] Verify `docker build -t hey-app:test .`.
- [ ] Verify the image contains and can start through `docker/entrypoint.sh`.
- [x] Append handoff notes and attempt to commit the implementation.

## Verification Notes
- `python3 -m unittest discover -s tests -v` verifies the Docker artifact contract in this sandbox.
- `docker build -t hey-app:test .` is blocked in this sandbox by Docker daemon socket access: `connect: operation not permitted`.
- Container startup through the built image needs to be verified in an environment with Docker daemon access.
- `git add`/`git commit` are blocked in this sandbox because writing `.git/index.lock` fails with `Operation not permitted`.

## Out of Scope
- Replacing `docker-compose.yml` with app and Postgres services.
- Adding or modifying `.env.example`.
- Changing API endpoints, payloads, auth, errors, or webhooks.
- Configuring Cloudflare Tunnel or host-level deployment services.

---

# Plan — Replace Compose With App And Postgres Deployment

## Goal
Make `docker compose up -d --build` run the complete local Hey deployment stack with a Django app service, PostgreSQL database service, loopback app port `9600`, deployment environment defaults, and persistent Postgres data.

## Checklist
- [x] Confirm the current Compose shape before editing.
- [x] Add a failing deployment contract test for the Compose and `.env.example` requirements.
- [x] Replace `docker-compose.yml` with `app` and `db` services, healthcheck, loopback port, deployment environment, and named Postgres volume.
- [x] Replace `.env.example` with local development and Docker deployment variables.
- [x] Update human-facing deployment docs and changelog for the Compose stack.
- [x] Run fresh verification for the deployment contract test and Compose acceptance criteria.
- [x] Append handoff notes and attempt to commit the implementation.

## Verification Notes
- `python3 -m unittest discover -s tests -v` passes with 2 tests.
- `docker compose config --services` prints `db` and `app`.
- `docker compose config --volumes` prints `postgres_data`.
- `docker compose config --no-interpolate` renders `host_ip: 127.0.0.1`, `published: "9600"`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_URL`, and the `postgres_data` volume.
- `docker compose up -d --build` is blocked in this sandbox by Docker daemon socket access: `connect: operation not permitted`.
- `git add` is blocked in this sandbox because writing `.git/index.lock` fails with `Operation not permitted`.

## Out of Scope
- Changing API endpoints, payloads, auth, errors, or webhooks.
- Configuring Cloudflare Tunnel, DNS, TLS, or host-level services.
- Building or running containers beyond Compose configuration validation in this task.
