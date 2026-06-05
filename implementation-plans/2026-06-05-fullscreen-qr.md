# Fullscreen QR Implementation Plan

> **For executing agents:** Apply the `subagent-driven-development` skill (recommended) or `executing-plans` skill to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an authenticated full-viewport page that shows a card's name and large QR code.

**Architecture:** Add one owner-protected Django `DetailView` in the existing `cards` app. The new HTML page reuses the current `cards:qr` PNG endpoint so QR generation and authorization stay centralized.

**Tech Stack:** Django 5.2 class-based views, Django templates, existing shared CSS in `static/css/app.css`, Django `TestCase`.

**Relevant Alfreds agents:** coding owns Tasks 1-3; testing owns Task 4.

---

## File Structure

- `cards/views.py` — add `CardQRFullscreenView` using `OwnedCardsMixin`.
- `cards/urls.py` — add the trailing-slash `cards:qr_fullscreen` route.
- `cards/templates/cards/card_qr_fullscreen.html` — create the standalone full-viewport QR page.
- `cards/templates/cards/card_detail.html` — add the entry link from the card detail actions.
- `static/css/app.css` — add focused fullscreen QR layout styles.
- `cards/tests.py` — add route, access-control, template, and detail-link tests.
- `API.md` — document the route, auth behavior, and response type.
- `docs/README.md` — link to the card feature documentation.
- `docs/features/cards.md` — create human-facing card feature documentation.
- `docs/CHANGELOG.md` — record the user-visible fullscreen QR feature.

---

### Task 1: Add Fullscreen QR Route And Page

**Files:**
- Modify: `cards/tests.py`
- Modify: `cards/views.py`
- Modify: `cards/urls.py`
- Create: `cards/templates/cards/card_qr_fullscreen.html`
- Modify: `static/css/app.css`

**Assigned agent:** coding

- [ ] **Step 1: Write failing tests for the fullscreen QR route**

Add these methods inside `CardFlowTests` in `cards/tests.py`, after `test_qr_png_and_vcf`:

```python
    def test_qr_fullscreen_page_requires_login(self):
        card = BusinessCard.objects.create(
            owner=self.user,
            first_name="Ada",
            last_name="Lovelace",
        )
        url = reverse("cards:qr_fullscreen", args=[card.pk])

        resp = self.client.get(url)

        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp.url)
        self.assertIn(url, resp.url)

    def test_qr_fullscreen_page_renders_owner_card(self):
        self.client.force_login(self.user)
        card = BusinessCard.objects.create(
            owner=self.user,
            first_name="Ada",
            last_name="Lovelace",
            organization="Analytical Engines",
            title="Founder",
        )

        resp = self.client.get(reverse("cards:qr_fullscreen", args=[card.pk]))

        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "cards/card_qr_fullscreen.html")
        self.assertContains(resp, "Ada Lovelace")
        self.assertContains(resp, "Founder · Analytical Engines")
        self.assertContains(resp, reverse("cards:qr", args=[card.pk]))
        self.assertContains(resp, reverse("cards:detail", args=[card.pk]))
        self.assertContains(resp, "Download QR")
        self.assertContains(resp, "qr-fullscreen__tile")

    def test_qr_fullscreen_page_hides_other_users_card(self):
        other = User.objects.create_user("charles", password=PW)
        card = BusinessCard.objects.create(
            owner=other,
            first_name="Charles",
            last_name="Babbage",
        )
        self.client.force_login(self.user)

        resp = self.client.get(reverse("cards:qr_fullscreen", args=[card.pk]))

        self.assertEqual(resp.status_code, 404)
```

- [ ] **Step 2: Run the new route tests to verify they fail**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_qr_fullscreen_page_requires_login cards.tests.CardFlowTests.test_qr_fullscreen_page_renders_owner_card cards.tests.CardFlowTests.test_qr_fullscreen_page_hides_other_users_card -v 2
```

Expected: FAIL with `django.urls.exceptions.NoReverseMatch: Reverse for 'qr_fullscreen' not found`.

- [ ] **Step 3: Add the owner-protected view**

In `cards/views.py`, add this class immediately after `CardDetailView`:

```python
class CardQRFullscreenView(OwnedCardsMixin, DetailView):
    template_name = "cards/card_qr_fullscreen.html"
    context_object_name = "card"
```

- [ ] **Step 4: Add the URL route**

In `cards/urls.py`, add this route immediately after the detail route:

```python
    path("cards/<int:pk>/qr/fullscreen/", views.CardQRFullscreenView.as_view(), name="qr_fullscreen"),
```

The surrounding route list should include:

```python
urlpatterns = [
    path("", views.CardListView.as_view(), name="list"),
    path("cards/new/", views.CardCreateView.as_view(), name="create"),
    path("cards/<int:pk>/", views.CardDetailView.as_view(), name="detail"),
    path("cards/<int:pk>/qr/fullscreen/", views.CardQRFullscreenView.as_view(), name="qr_fullscreen"),
    path("cards/<int:pk>/edit/", views.CardUpdateView.as_view(), name="edit"),
    path("cards/<int:pk>/delete/", views.CardDeleteView.as_view(), name="delete"),
    path("cards/<int:pk>/qr.png", views.card_qr_png, name="qr"),
    path("cards/<int:pk>/vcard.vcf", views.card_vcf, name="vcf"),
]
```

- [ ] **Step 5: Create the fullscreen template**

Create `cards/templates/cards/card_qr_fullscreen.html` with this exact content:

```django
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ card.display_name|default:card.full_label }} QR · hey</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Hanken+Grotesk:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body class="qr-fullscreen-body">
  <main class="qr-fullscreen">
    <div class="qr-fullscreen__actions" aria-label="QR actions">
      <a class="btn btn--ghost btn--sm" href="{% url 'cards:detail' card.pk %}">Back to card</a>
      <a class="btn btn--sm" href="{% url 'cards:qr' card.pk %}" download="{{ card.display_name|default:'contact' }}-qr.png">Download QR</a>
    </div>

    <section class="qr-fullscreen__content" aria-labelledby="qr-fullscreen-title">
      <span class="kicker">Contact QR</span>
      <h1 id="qr-fullscreen-title">{{ card.display_name|default:card.full_label }}</h1>
      {% if card.role_line %}<p class="qr-fullscreen__role">{{ card.role_line }}</p>{% endif %}
      <div class="qr-fullscreen__tile">
        <img src="{% url 'cards:qr' card.pk %}" alt="QR code for {{ card.display_name|default:card.full_label }}">
      </div>
    </section>
  </main>
</body>
</html>
```

- [ ] **Step 6: Add fullscreen layout styles**

Append this CSS to `static/css/app.css` before the existing `@media (max-width:760px)` block:

```css
/* ---- fullscreen QR ---- */
body.qr-fullscreen-body{
  min-height:100vh;
  background:var(--paper);
}
body.qr-fullscreen-body::after{
  background:
    radial-gradient(900px 600px at 15% 0%, rgba(189,75,44,0.08), transparent 60%),
    radial-gradient(800px 700px at 100% 100%, rgba(30,90,78,0.06), transparent 60%);
}
.qr-fullscreen{
  position:relative;
  z-index:2;
  min-height:100vh;
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  padding:96px clamp(18px,5vw,40px) 56px;
}
.qr-fullscreen__actions{
  position:fixed;
  top:24px;
  left:clamp(18px,5vw,40px);
  right:clamp(18px,5vw,40px);
  z-index:4;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  pointer-events:none;
}
.qr-fullscreen__actions .btn{
  pointer-events:auto;
}
.qr-fullscreen__content{
  width:min(92vw,760px);
  display:flex;
  flex-direction:column;
  align-items:center;
  text-align:center;
}
.qr-fullscreen__content .kicker{
  margin-bottom:18px;
}
.qr-fullscreen__content .kicker::before{
  display:none;
}
.qr-fullscreen__content h1{
  max-width:14ch;
  font-size:4.5rem;
  overflow-wrap:anywhere;
}
.qr-fullscreen__role{
  margin-top:18px;
  font-family:'Space Mono',monospace;
  font-size:13px;
  letter-spacing:.08em;
  text-transform:uppercase;
  color:var(--accent);
  overflow-wrap:anywhere;
}
.qr-fullscreen__tile{
  width:min(76vmin,560px);
  aspect-ratio:1;
  margin-top:34px;
  padding:clamp(12px,2vw,22px);
  background:#fff;
  border-radius:12px;
  box-shadow:0 24px 60px -34px var(--shadow), inset 0 0 0 1px var(--line-soft);
  line-height:0;
}
.qr-fullscreen__tile img{
  width:100%;
  height:100%;
  display:block;
  object-fit:contain;
}
```

Then add this nested block inside the existing `@media (max-width:760px)` block:

```css
  .qr-fullscreen{
    justify-content:flex-start;
    padding-top:112px;
  }
  .qr-fullscreen__actions{
    position:absolute;
    top:18px;
    left:18px;
    right:18px;
  }
  .qr-fullscreen__content h1{
    font-size:2.6rem;
  }
  .qr-fullscreen__tile{
    width:min(84vmin,420px);
    margin-top:26px;
  }
```

- [ ] **Step 7: Run the fullscreen route tests again**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_qr_fullscreen_page_requires_login cards.tests.CardFlowTests.test_qr_fullscreen_page_renders_owner_card cards.tests.CardFlowTests.test_qr_fullscreen_page_hides_other_users_card -v 2
```

Expected: all 3 tests PASS.

- [ ] **Step 8: Commit the route and fullscreen page**

Run:

```bash
git add cards/tests.py cards/views.py cards/urls.py cards/templates/cards/card_qr_fullscreen.html static/css/app.css
git commit -m "feat: add fullscreen QR page"
```

Expected: commit succeeds with the new view, route, template, styles, and tests.

---

### Task 2: Add Detail Page Entry Point

**Files:**
- Modify: `cards/tests.py`
- Modify: `cards/templates/cards/card_detail.html`

**Assigned agent:** coding

- [ ] **Step 1: Write the failing detail-page link test**

Add this method inside `CardFlowTests` in `cards/tests.py`, after `test_qr_fullscreen_page_renders_owner_card`:

```python
    def test_detail_page_links_to_qr_fullscreen(self):
        self.client.force_login(self.user)
        card = BusinessCard.objects.create(
            owner=self.user,
            first_name="Ada",
            last_name="Lovelace",
        )

        resp = self.client.get(reverse("cards:detail", args=[card.pk]))

        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Fullscreen QR")
        self.assertContains(resp, reverse("cards:qr_fullscreen", args=[card.pk]))
        self.assertContains(resp, reverse("cards:vcf", args=[card.pk]))
        self.assertContains(resp, reverse("cards:qr", args=[card.pk]))
```

- [ ] **Step 2: Run the detail-page link test to verify it fails**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_detail_page_links_to_qr_fullscreen -v 2
```

Expected: FAIL because `Fullscreen QR` is not present in `cards/card_detail.html`.

- [ ] **Step 3: Add the fullscreen action to the detail page**

In `cards/templates/cards/card_detail.html`, replace this action block:

```django
  <div class="btn-row">
    <a class="btn" href="{% url 'cards:vcf' card.pk %}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>
      Download .vcf
    </a>
    <a class="btn btn--ghost" href="{% url 'cards:qr' card.pk %}" download="{{ card.display_name|default:'contact' }}-qr.png">Download QR (PNG)</a>
    <span class="hint">Scan with a phone camera to add the contact</span>
  </div>
```

with this block:

```django
  <div class="btn-row">
    <a class="btn" href="{% url 'cards:vcf' card.pk %}">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M7 10l5 5 5-5"/><path d="M12 15V3"/></svg>
      Download .vcf
    </a>
    <a class="btn btn--ghost" href="{% url 'cards:qr_fullscreen' card.pk %}">Fullscreen QR</a>
    <a class="btn btn--ghost" href="{% url 'cards:qr' card.pk %}" download="{{ card.display_name|default:'contact' }}-qr.png">Download QR (PNG)</a>
    <span class="hint">Scan with a phone camera to add the contact</span>
  </div>
```

- [ ] **Step 4: Run the detail-page link test again**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_detail_page_links_to_qr_fullscreen -v 2
```

Expected: PASS.

- [ ] **Step 5: Commit the detail entry point**

Run:

```bash
git add cards/tests.py cards/templates/cards/card_detail.html
git commit -m "feat: link detail page to fullscreen QR"
```

Expected: commit succeeds with the detail-page action and test.

---

### Task 3: Document Fullscreen QR

**Files:**
- Modify: `API.md`
- Modify: `docs/README.md`
- Create: `docs/features/cards.md`
- Modify: `docs/CHANGELOG.md`

**Assigned agent:** coding

- [ ] **Step 1: Update the API contract**

Replace the contents of `API.md` with:

````markdown
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
| GET | `/cards/<id>/qr/fullscreen/` | Show a full-viewport HTML QR presentation page with the card name. | Authenticated owner |
| GET | `/cards/<id>/qr.png` | Return a PNG QR code containing the card's vCard data. | Authenticated owner |
| GET | `/cards/<id>/vcard.vcf` | Return the card as a downloadable vCard file. | Authenticated owner |

## Request / Response Shapes

HTML routes return Django-rendered HTML. `/cards/<id>/qr.png` returns `image/png` with `Cache-Control: no-store`. `/cards/<id>/vcard.vcf` returns `text/vcard; charset=utf-8` with an attachment filename derived from the card display name.

## Error Model

Unauthenticated users are redirected to `/accounts/login/` for class-based card pages. Card download helper endpoints return HTTP 404 for unauthenticated requests and for requests to cards the user does not own. Authenticated users receive HTTP 404 for other users' cards.

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

Successful response: HTTP 200 with an HTML page containing the card display name and an `<img>` that references `/cards/12/qr.png`.
````

- [ ] **Step 2: Create the card feature documentation**

Create `docs/features/cards.md` with:

```markdown
# Cards

Hey cards store a person's contact details and can be viewed, downloaded, and shared as QR codes.

## Card List

Authenticated users land on the card list at `/`. The list only shows cards owned by the current user.

## Card Detail

Each card detail page at `/cards/<id>/` shows the display name, role line, contact fields, QR preview, vCard data, and card actions.

## QR Codes

The QR PNG endpoint at `/cards/<id>/qr.png` encodes the card's vCard data and is only available to the card owner. The detail page uses this endpoint for its QR preview and PNG download.

The fullscreen QR page at `/cards/<id>/qr/fullscreen/` shows the card name and a large QR code in a focused layout. It is intended for presenting a card from a phone, tablet, or display while keeping the normal detail page available for editing and downloads.

## vCard Downloads

The vCard endpoint at `/cards/<id>/vcard.vcf` returns a downloadable `.vcf` file generated from the same card fields used by the QR code.

## Access Control

All card pages and download endpoints are scoped to the logged-in owner. Users cannot view, edit, delete, download, or present another user's card.
```

- [ ] **Step 3: Update the docs index**

In `docs/README.md`, replace the documentation map with:

```markdown
## Documentation map

- `docs/architecture.md` — high-level system shape and data flow.
- `docs/features/cards.md` — card viewing, QR, fullscreen QR, and download behavior.
- `docs/features/deployment.md` — localhost Docker Compose deployment.
- `docs/CHANGELOG.md` — notable user-visible changes.
```

- [ ] **Step 4: Update the changelog**

Add this entry at the top of `docs/CHANGELOG.md`, immediately after `# Changelog`:

```markdown
## 2026-06-05 — Add fullscreen QR page
- Add an owner-protected fullscreen QR page for presenting a card name and large QR code.
- Add a `Fullscreen QR` action from the card detail page.

```

- [ ] **Step 5: Review the docs diff**

Run:

```bash
git diff -- API.md docs/README.md docs/features/cards.md docs/CHANGELOG.md
```

Expected: diff shows only the API contract, docs index, card feature doc, and changelog updates described in this task.

- [ ] **Step 6: Commit the docs**

Run:

```bash
git add API.md docs/README.md docs/features/cards.md docs/CHANGELOG.md
git commit -m "docs: document fullscreen QR page"
```

Expected: commit succeeds with the API and human-facing documentation updates.

---

### Task 4: Verify Fullscreen QR End To End

**Files:**
- No planned file edits.

**Assigned agent:** testing

- [ ] **Step 1: Run the card test suite**

Run:

```bash
python manage.py test cards -v 2
```

Expected: all `cards` tests PASS, including:

```text
test_qr_fullscreen_page_requires_login
test_qr_fullscreen_page_renders_owner_card
test_qr_fullscreen_page_hides_other_users_card
test_detail_page_links_to_qr_fullscreen
```

- [ ] **Step 2: Run the full Django test suite**

Run:

```bash
python manage.py test -v 2
```

Expected: all tests PASS.

- [ ] **Step 3: Verify the route name resolves**

Run:

```bash
python manage.py shell -c "from django.urls import reverse; print(reverse('cards:qr_fullscreen', args=[1]))"
```

Expected output:

```text
/cards/1/qr/fullscreen/
```

- [ ] **Step 4: Inspect the final diff**

Run:

```bash
git status --short
git diff --check
```

Expected: `git diff --check` prints no whitespace errors. `git status --short` is empty if the previous task commits were created successfully.

- [ ] **Step 5: Report verification**

Post a concise summary with:

```text
Verification complete:
- cards tests: pass
- full Django tests: pass
- route resolution: /cards/1/qr/fullscreen/
- whitespace check: pass
```
