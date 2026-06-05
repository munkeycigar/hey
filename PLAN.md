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
