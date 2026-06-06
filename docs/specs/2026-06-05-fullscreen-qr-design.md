# Project: Hey Fullscreen QR Page

## Overview

Add a dedicated full-viewport QR presentation page for an authenticated user's business card. The page should fit a mobile screen cleanly, show the card name and a large QR code, and look intentional when the user presents it from a phone, tablet, or external display.

## Requirements

- Provide an owner-protected, trailing-slash Django route for fullscreen QR presentation.
- Render the selected card's display name prominently with a large QR image below it.
- Use a presentation-display layout: no normal site chrome, polished visual treatment, mobile-safe viewport sizing, and compact controls that do not compete with the QR code.
- Fit common mobile screens without awkward vertical overflow by using safe viewport units and safe-area padding.
- Make long card names and role lines wrap cleanly without overlapping the QR code or controls.
- Reuse the existing QR PNG endpoint so QR generation behavior stays centralized.
- Add an obvious entry point from the existing card detail page.
- Keep the normal card detail, QR PNG download, and vCard download behavior unchanged.
- Document the new user-facing endpoint in `API.md` and human-facing docs.

## Technical Stack

- Backend: Django 5.2 class-based views, URL routing, templates, and session auth.
- Frontend: Existing server-rendered templates plus shared CSS in `static/css/app.css`.
- Data: Existing `cards.BusinessCard` model and `display_name` / `full_label` properties.
- QR: Existing `cards:qr` PNG route backed by `card_qr_png()`.

## Architecture

The feature adds one HTML view in the existing `cards` app, using the same owner-filtering pattern as `CardDetailView`. The new page should not create a new QR generation path; it should display an `<img>` whose source is `{% url 'cards:qr' card.pk %}`. This keeps QR generation, caching headers, and owner isolation behavior in one place.

The route should be a normal Django route with a trailing slash, for example `cards/<int:pk>/qr/fullscreen/`, named `cards:qr_fullscreen`. Authentication and ownership should match the existing detail page: unauthenticated users are redirected to login through `LoginRequiredMixin`, and authenticated non-owners receive a 404.

The fullscreen template should be standalone rather than extending the normal app shell. Its CSS should prioritize mobile presentation: `min-height:100svh`, safe-area-aware padding, a constrained content stack, high-contrast QR framing, and responsive sizing that keeps the name, role line, QR tile, and controls visible on narrow screens. Desktop should use the same page as a centered presentation display, with a larger QR tile but no decorative layout that distracts from scanning.

## Features

### Feature 1: Fullscreen QR Presentation

- Description: A focused page for showing a selected card's name and QR code at presentation size.
- Acceptance Criteria:
  - [ ] Visiting the fullscreen URL while logged in as the card owner returns HTTP 200.
  - [ ] The page title and visible heading include `card.display_name|default:card.full_label`.
  - [ ] The page contains a large QR image using the existing `cards:qr` URL.
  - [ ] The layout uses a presentation-display treatment that looks polished on phone, tablet, and desktop displays.
  - [ ] The layout uses mobile-safe viewport sizing and safe-area padding so the page fits common mobile screens.
  - [ ] Long card names and role lines wrap cleanly without overlapping the QR code or action controls.
  - [ ] The page includes a restrained back link to the card detail page and a download link for the QR PNG.

### Feature 2: Detail Page Entry Point

- Description: The existing card detail page should expose a clear action to open the fullscreen QR page.
- Acceptance Criteria:
  - [ ] Card detail pages include a `Fullscreen QR` link or button near the existing QR actions.
  - [ ] The link targets the new `cards:qr_fullscreen` route.
  - [ ] Existing `Download .vcf` and `Download QR (PNG)` actions remain available.

### Feature 3: Access Control Coverage

- Description: The fullscreen page must follow the same ownership rules as other card views.
- Acceptance Criteria:
  - [ ] Anonymous requests to the fullscreen page redirect to the login page.
  - [ ] A logged-in user cannot view another user's fullscreen QR page.
  - [ ] Existing QR PNG and vCard tests continue to pass.

### Feature 4: Documentation

- Description: Maintain the project docs and API contract so future maintainers know the route exists.
- Acceptance Criteria:
  - [ ] `API.md` lists the fullscreen QR HTML route, auth behavior, and purpose.
  - [ ] Human-facing docs mention the fullscreen QR page where card features are documented.
  - [ ] `docs/CHANGELOG.md` records the new user-visible feature.

## Integration Map

| Feature | Reads from | Writes to / Affects |
|---------|------------|---------------------|
| Fullscreen QR Presentation | `BusinessCard.display_name`, `BusinessCard.full_label`, existing `cards:qr` PNG endpoint | Adds a new HTML page for a single owned card; does not mutate data |
| Detail Page Entry Point | Existing card detail context and route names | Adds navigation from card detail to the fullscreen page |
| Access Control Coverage | Existing owner isolation conventions in `OwnedCardsMixin` | Confirms fullscreen access mirrors card detail access |
| Documentation | Existing route/API conventions and user-facing docs | Updates API/docs/changelog to reflect the endpoint |

## Implementation Planning Notes

- Create `CardQRFullscreenView` in `cards/views.py` using `OwnedCardsMixin` and `DetailView`.
- Add `path("cards/<int:pk>/qr/fullscreen/", views.CardQRFullscreenView.as_view(), name="qr_fullscreen")` in `cards/urls.py`.
- Create `cards/templates/cards/card_qr_fullscreen.html`.
- Add CSS classes for the presentation-display fullscreen layout in `static/css/app.css`, including `100svh`, safe-area padding, responsive QR sizing, and long-text wrapping.
- Add tests to `cards/tests.py` for authenticated owner access, login redirect, owner isolation, QR image URL rendering, and the presentation layout hook.
- Create `docs/features/cards.md` to describe card viewing, QR, fullscreen QR, and download behavior.
- Update `API.md` and `docs/CHANGELOG.md`.

## Questions / Clarifications Needed

- None. The approved interaction is a dedicated full-viewport page using the presentation-display direction.
