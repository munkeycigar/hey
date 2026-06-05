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

---

# Plan — Document Localhost Deployment

## Goal
Document how maintainers deploy Hey locally on `127.0.0.1:9600` for an external Cloudflare Tunnel origin.

## Checklist
- [x] Update `README.md` with Docker deployment start, verify, logs, update, and stop commands.
- [x] Update `docs/README.md` as the human-facing documentation index.
- [x] Update `docs/architecture.md` with the localhost Compose and external tunnel architecture.
- [x] Update `docs/features/deployment.md` with the deployment guide and required commands.
- [x] Add a dated `docs/CHANGELOG.md` entry for the deployment documentation.
- [x] Update `ARCHITECTURE.md` with the canonical Cloudflare Tunnel origin setup.
- [x] Verify the documentation covers the acceptance criteria and command examples.
- [x] Append handoff notes and attempt to commit the documentation changes.

## Verification Notes
- `rg -n "Cloudflare Tunnel|http://127\\.0\\.0\\.1:9600|docker compose up -d --build|docker compose logs -f app|git pull|docker compose down" README.md docs/README.md docs/architecture.md docs/features/deployment.md docs/CHANGELOG.md ARCHITECTURE.md` confirms the required documentation coverage.
- `git diff --check` passes.
- `python3 -m unittest discover -s tests -v` passes with 2 tests.
- `git add README.md docs/README.md docs/architecture.md docs/features/deployment.md docs/CHANGELOG.md ARCHITECTURE.md PLAN.md HANDOFF.md && git commit -m "docs: document localhost compose deployment"` is blocked in this sandbox because `.git/index.lock` cannot be created: `Operation not permitted`.

## Out of Scope
- Changing Docker Compose behavior or application runtime code.
- Configuring Cloudflare Tunnel, DNS, TLS, or host-level services.
- Changing API endpoints, payloads, auth, errors, or webhooks.

---

# Plan — Add Fullscreen QR Route And Page

## Goal
Add an authenticated owner-protected full-viewport QR page for business cards.

## Checklist
- [x] Add failing tests for the fullscreen QR route login, owner rendering, and owner isolation behavior.
- [x] Verify the new fullscreen QR route tests fail before production code changes.
- [x] Add the owner-protected fullscreen QR view and trailing-slash URL route.
- [x] Create the standalone fullscreen QR template.
- [x] Add focused fullscreen QR CSS with responsive mobile rules.
- [x] Update human-facing docs and API route documentation for the fullscreen QR page.
- [x] Run targeted fullscreen QR tests and the cards test suite.
- [x] Run route resolution and whitespace verification.
- [x] Append handoff notes and attempt to commit the implementation.

## Verification Notes
- Red test run: the three new fullscreen QR tests failed with `NoReverseMatch` for `cards:qr_fullscreen` before production code was added.
- Green targeted run: the three fullscreen QR tests passed under a constrained Django harness using SQLite plus import shims for unavailable offline packages.
- Green suite run: `cards` and full Django discovery each passed 10 tests under the same constrained harness.
- Route resolution printed `/cards/1/qr/fullscreen/`.
- `python3 -m compileall accounts cards config manage.py` passed.
- `git diff --check` passed.
- Unshimmed `.venv/bin/python manage.py test ...` is blocked because the local virtualenv lacks Django, and `pip install -r requirements.txt` is blocked by sandbox network/DNS restrictions.
- `git add ... && git commit -m "feat: add fullscreen QR page"` is blocked because the sandbox cannot create `.git/index.lock` (`Operation not permitted`).

## Integration Check
- Existing QR displays and downloads continue to use `cards:qr`.
- The card detail page entry point is a planned Task 2 follow-up and remains out of scope for this Task 1 implementation.

## Out of Scope
- Adding the card detail page entry point to fullscreen QR.
- Changing QR PNG generation or vCard serialization.
- Changing account authentication behavior.

---

# Plan — Link Detail Page To Fullscreen QR

## Goal
Add a clear Fullscreen QR action on the card detail page while preserving existing vCard and QR PNG download actions.

## Checklist
- [x] Add a failing detail-page test for the fullscreen QR link and existing download actions.
- [x] Verify the new detail-page link test fails before production template changes.
- [x] Add the Fullscreen QR action to the card detail page.
- [x] Update human-facing docs and changelog for the detail-page action.
- [x] Run targeted and relevant regression tests.
- [x] Run integration checks for related card actions.
- [x] Append handoff notes.
- [ ] Commit the implementation.

## Verification Notes
- Red test run: `test_detail_page_links_to_qr_fullscreen` failed because `Fullscreen QR` was missing from the card detail response.
- Green targeted run: `test_detail_page_links_to_qr_fullscreen` passed under the constrained Django harness using SQLite and local import shims.
- Regression run: `python3 manage.py test cards -v 2` passed 11 tests under the same constrained Django harness.
- Repository artifact tests: `python3 -m unittest discover -s tests -v` passed 2 tests.
- Syntax check: `python3 -m compileall accounts cards config manage.py` passed.
- Whitespace check: `git diff --check` passed.
- Unshimmed Django test commands are blocked because this workspace `.venv` lacks Django and sandbox DNS blocks `pip install -r requirements.txt`.
- Commit is blocked in this sandbox because Git cannot create `.git/index.lock`: `Operation not permitted`.

## Integration Check
- Card detail now links to `cards:qr_fullscreen`.
- Existing `cards:vcf` and `cards:qr` card detail actions remain in the same action row.
- No records are created or updated by this task, and no other feature needs to react to new data.

## Out of Scope
- Changing the fullscreen QR route, view, template, or styles from Task 1.
- Changing QR PNG generation or vCard serialization.
- Changing API endpoints, payloads, auth behavior, errors, or webhooks.
