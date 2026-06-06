# Changelog

## 2026-06-06 — Improve fullscreen QR presentation
- Improve the fullscreen QR page with mobile-safe viewport sizing and a polished presentation-display layout.

## 2026-06-05 — Link card detail to fullscreen QR
- Add a Fullscreen QR action to card detail pages while keeping `.vcf` and PNG downloads available.

## 2026-06-05 — Add fullscreen QR page
- Add an owner-protected fullscreen QR page for presenting a card name and large QR code.

## 2026-06-05 — Document localhost deployment
- Document how maintainers deploy Hey on `127.0.0.1:9600` behind an existing Cloudflare Tunnel.

## 2026-06-05 — Add Compose app and PostgreSQL deployment
- Run the local Docker deployment with `app` and `db` services.
- Bind the app to `127.0.0.1:9600` and persist PostgreSQL data in `postgres_data`.

## 2026-06-05 — Add Docker app image
- Add a Docker build path and entrypoint for the Django app container.
- Document the Docker image behavior and build context exclusions.
