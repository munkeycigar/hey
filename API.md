# API — Hey

_API surface contract for this project. Both human developers and AI agents should read this before changing endpoints, payloads, auth, or anything a caller depends on. Keep it current as the API evolves._

> Companion to [`ARCHITECTURE.md`](./ARCHITECTURE.md), which covers the broader system map.

## Overview

Hey is a server-rendered Django app for virtual business cards. The app exposes authenticated HTML pages for card management plus download endpoints for card vCards and QR PNGs.

## Authentication

Hey uses Django session authentication. Card routes require a logged-in user unless noted otherwise. Card-specific routes are owner-isolated: authenticated users receive HTTP 404 when they request another user's card.

## Endpoints

### Accounts

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET/POST | `/accounts/register/` | Register a new user and log them in. | Anonymous |
| GET/POST | `/accounts/login/` | Start a user session. | Anonymous |
| POST | `/accounts/logout/` | End the current user session. | Authenticated |

### Cards

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| GET | `/` | List the current user's cards. | Authenticated |
| GET/POST | `/cards/new/` | Create a card owned by the current user. | Authenticated |
| GET | `/cards/<id>/` | Show one owned card. | Authenticated owner |
| GET/POST | `/cards/<id>/edit/` | Edit one owned card. | Authenticated owner |
| GET/POST | `/cards/<id>/delete/` | Delete one owned card. | Authenticated owner |
| GET | `/cards/<id>/qr/fullscreen/` | Show a mobile-first full-viewport HTML QR presentation page with the card name. | Authenticated owner |
| GET | `/cards/<id>/qr.png` | Return a PNG QR code containing the card's vCard data. | Authenticated owner |
| GET | `/cards/<id>/vcard.vcf` | Return the card as a downloadable vCard file. | Authenticated owner |

## Request / Response Shapes

HTML routes return Django-rendered HTML. `/cards/<id>/qr/fullscreen/` returns a mobile-first presentation HTML page containing the card display name and an image that references `/cards/<id>/qr.png`. `/cards/<id>/qr.png` returns `image/png` with `Cache-Control: no-store`. `/cards/<id>/vcard.vcf` returns `text/vcard; charset=utf-8` with an attachment filename derived from the card display name.

## Error Model

Unauthenticated users are redirected to `/accounts/login/` for class-based card pages, including `/cards/<id>/qr/fullscreen/`. Card download helper endpoints return HTTP 404 for unauthenticated requests and for requests to cards the user does not own. Authenticated users receive HTTP 404 for other users' cards.

## Webhooks / Events

Hey does not emit webhooks or outbound events.

## Rate Limits

No application-level rate limits are configured.

## Versioning

The app does not expose a versioned public API. Endpoint changes are tracked in this file and in `docs/CHANGELOG.md`.

## Examples

```http
GET /cards/12/qr/fullscreen/ HTTP/1.1
Host: hey.leorey.es
Cookie: sessionid=...
```

Successful response: HTTP 200 with a mobile-first HTML presentation page containing the card display name and an `<img>` that references `/cards/12/qr.png`.
