# Fullscreen QR Presentation Display Implementation Plan

> **For executing agents:** Apply the `subagent-driven-development` skill (recommended) or `executing-plans` skill to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the fullscreen QR page so it fits mobile screens and reads as a polished presentation display with the card name and QR code.

**Architecture:** Keep the existing authenticated `cards:qr_fullscreen` Django route and continue reusing the `cards:qr` PNG endpoint. Update the standalone fullscreen template and shared CSS so the page uses mobile-safe viewport sizing, safe-area padding, long-name handling, and compact controls that do not compete with scanning.

**Tech Stack:** Django 5.2 class-based views, Django templates, existing shared CSS in `static/css/app.css`, Django `TestCase`.

**Relevant Alfreds agents:** coding owns Tasks 1-2; testing/QA owns Task 3.

---

## File Structure

- `cards/tests.py` — strengthen fullscreen QR assertions for the presentation-display layout hook.
- `cards/templates/cards/card_qr_fullscreen.html` — replace the first-pass utility layout with a mobile-first presentation page.
- `static/css/app.css` — replace fullscreen QR styles with mobile-safe `100svh` layout, constrained QR sizing, and polished display treatment.
- `API.md` — clarify the fullscreen route returns a mobile presentation page.
- `docs/features/cards.md` — document the presentation-display behavior.
- `docs/CHANGELOG.md` — record the design improvement.

---

### Task 1: Upgrade Fullscreen QR Presentation Layout

**Files:**
- Modify: `cards/tests.py`
- Modify: `cards/templates/cards/card_qr_fullscreen.html`
- Modify: `static/css/app.css`

**Assigned agent:** coding

- [ ] **Step 1: Update the fullscreen page test**

In `cards/tests.py`, replace `test_qr_fullscreen_page_renders_owner_card` with:

```python
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
        self.assertContains(resp, "Download")
        self.assertContains(resp, "viewport-fit=cover")
        self.assertContains(resp, "qr-fullscreen--presentation")
        self.assertContains(resp, "qr-fullscreen__qr-card")
```

- [ ] **Step 2: Run the focused test and verify the current page fails the new design assertions**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_qr_fullscreen_page_renders_owner_card -v 2
```

Expected before implementation: FAIL because the first-pass template does not include `viewport-fit=cover`, `qr-fullscreen--presentation`, and `qr-fullscreen__qr-card`.

- [ ] **Step 3: Replace the fullscreen template**

Replace `cards/templates/cards/card_qr_fullscreen.html` with:

```django
{% load static %}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
  <title>{{ card.display_name|default:card.full_label }} QR · hey</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=Hanken+Grotesk:wght@400;500;600&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body class="qr-fullscreen-body">
  <main class="qr-fullscreen qr-fullscreen--presentation">
    <div class="qr-fullscreen__actions" aria-label="QR actions">
      <a class="btn btn--ghost btn--sm" href="{% url 'cards:detail' card.pk %}">Back</a>
      <a class="btn btn--sm" href="{% url 'cards:qr' card.pk %}" download="{{ card.display_name|default:'contact' }}-qr.png">Download</a>
    </div>

    <section class="qr-fullscreen__stage" aria-labelledby="qr-fullscreen-title">
      <span class="qr-fullscreen__eyebrow">hey contact</span>
      <h1 id="qr-fullscreen-title" title="{{ card.display_name|default:card.full_label }}">{{ card.display_name|default:card.full_label }}</h1>
      {% if card.role_line %}<p class="qr-fullscreen__role">{{ card.role_line }}</p>{% endif %}
      <div class="qr-fullscreen__qr-card">
        <img src="{% url 'cards:qr' card.pk %}" alt="QR code for {{ card.display_name|default:card.full_label }}">
      </div>
    </section>
  </main>
</body>
</html>
```

- [ ] **Step 4: Replace the fullscreen QR CSS**

In `static/css/app.css`, remove the existing first-pass fullscreen QR block that starts at `/* ---- fullscreen QR ---- */`, including its nested mobile rules inside `@media (max-width:760px)`. Keep the existing non-QR mobile rules for `.form-grid`, `.preview-card`, and `.pc-qr`.

Insert this CSS before the existing `@media (max-width:760px)` block:

```css
/* ---- fullscreen QR presentation ---- */
body.qr-fullscreen-body{
  min-height:100vh;
  min-height:100svh;
  overflow:hidden;
  background:#10251f;
  color:#fffaf2;
}
body.qr-fullscreen-body::before{
  opacity:.14;
  mix-blend-mode:screen;
}
body.qr-fullscreen-body::after{
  background:
    linear-gradient(135deg, rgba(189,75,44,.22) 0%, rgba(189,75,44,0) 38%),
    linear-gradient(180deg, #10251f 0%, #142c26 58%, #efe9dd 58%, #efe9dd 100%);
}
.qr-fullscreen{
  position:relative;
  z-index:2;
  height:100vh;
  height:100svh;
  min-height:100svh;
  display:grid;
  grid-template-rows:auto minmax(0,1fr);
  gap:clamp(12px,2svh,22px);
  padding:
    max(16px, env(safe-area-inset-top))
    max(16px, env(safe-area-inset-right))
    max(18px, env(safe-area-inset-bottom))
    max(16px, env(safe-area-inset-left));
}
.qr-fullscreen__actions{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  min-width:0;
}
.qr-fullscreen__actions .btn{
  min-height:38px;
  padding:8px 12px;
  border-radius:8px;
  background:rgba(255,250,242,.94);
  color:#10251f;
  box-shadow:0 14px 34px -24px rgba(0,0,0,.7);
  font-size:13px;
  line-height:1;
  white-space:nowrap;
}
.qr-fullscreen__actions .btn--ghost{
  background:rgba(255,250,242,.08);
  color:#fffaf2;
  box-shadow:inset 0 0 0 1px rgba(255,250,242,.28);
}
.qr-fullscreen__stage{
  width:min(100%,720px);
  min-height:0;
  margin:0 auto;
  display:grid;
  grid-template-rows:auto auto auto minmax(0,1fr);
  align-content:center;
  justify-items:center;
  gap:clamp(10px,2svh,24px);
  text-align:center;
}
.qr-fullscreen__eyebrow{
  font-family:'Space Mono',monospace;
  font-size:12px;
  letter-spacing:0;
  text-transform:uppercase;
  color:rgba(255,250,242,.72);
}
.qr-fullscreen__stage h1{
  max-width:min(92vw,12ch);
  color:#fffaf2;
  font-size:clamp(2.4rem,9vw,5.8rem);
  line-height:.96;
  letter-spacing:0;
  overflow-wrap:anywhere;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
}
.qr-fullscreen__role{
  max-width:min(86vw,50ch);
  margin:0;
  font-family:'Space Mono',monospace;
  font-size:clamp(11px,2.4vw,14px);
  letter-spacing:0;
  text-transform:uppercase;
  color:rgba(255,250,242,.74);
  overflow-wrap:anywhere;
  display:-webkit-box;
  -webkit-line-clamp:2;
  -webkit-box-orient:vertical;
  overflow:hidden;
}
.qr-fullscreen__qr-card{
  width:min(76svmin,560px);
  max-width:100%;
  aspect-ratio:1;
  padding:clamp(12px,2.4svmin,24px);
  background:#fff;
  border-radius:8px;
  box-shadow:0 26px 70px -36px rgba(0,0,0,.72), inset 0 0 0 1px rgba(16,37,31,.12);
  line-height:0;
}
.qr-fullscreen__qr-card img{
  width:100%;
  height:100%;
  display:block;
  object-fit:contain;
}
```

Then add these QR-specific mobile rules inside the existing `@media (max-width:760px)` block, after `.pc-qr{align-self:center;}`:

```css
  .qr-fullscreen{
    gap:10px;
    padding:
      max(12px, env(safe-area-inset-top))
      max(12px, env(safe-area-inset-right))
      max(14px, env(safe-area-inset-bottom))
      max(12px, env(safe-area-inset-left));
  }
  .qr-fullscreen__actions{
    gap:8px;
  }
  .qr-fullscreen__actions .btn{
    min-height:36px;
    padding:8px 10px;
    font-size:12px;
  }
  .qr-fullscreen__stage{
    align-content:start;
    padding-top:clamp(8px,2svh,18px);
    gap:clamp(8px,1.6svh,14px);
  }
  .qr-fullscreen__stage h1{
    max-width:11ch;
    font-size:clamp(2rem,11vw,3.3rem);
  }
  .qr-fullscreen__qr-card{
    width:min(84vw,47svh,380px);
    padding:clamp(10px,3vw,16px);
  }
```

Add this short-height rule after the `@media (max-width:760px)` block:

```css
@media (max-height:700px){
  .qr-fullscreen__eyebrow{
    display:none;
  }
  .qr-fullscreen__stage h1{
    font-size:clamp(1.8rem,9svh,3.6rem);
  }
  .qr-fullscreen__role{
    font-size:11px;
  }
  .qr-fullscreen__qr-card{
    width:min(78vw,44svh,420px);
  }
}
```

- [ ] **Step 5: Run the focused fullscreen test**

Run:

```bash
python manage.py test cards.tests.CardFlowTests.test_qr_fullscreen_page_renders_owner_card -v 2
```

Expected: PASS.

- [ ] **Step 6: Run whitespace check for edited frontend files**

Run:

```bash
git diff --check cards/templates/cards/card_qr_fullscreen.html static/css/app.css cards/tests.py
```

Expected: no output.

- [ ] **Step 7: Commit the presentation display upgrade**

Run:

```bash
git add cards/tests.py cards/templates/cards/card_qr_fullscreen.html static/css/app.css
git commit -m "feat: improve fullscreen QR presentation"
```

Expected: commit succeeds with the test, template, and CSS changes.

---

### Task 2: Document Mobile Presentation Behavior

**Files:**
- Modify: `API.md`
- Modify: `docs/features/cards.md`
- Modify: `docs/CHANGELOG.md`

**Assigned agent:** coding

- [ ] **Step 1: Update the API response shape**

In `API.md`, replace this sentence:

```markdown
HTML routes return Django-rendered HTML. `/cards/<id>/qr/fullscreen/` returns an HTML page containing the card display name and an image that references `/cards/<id>/qr.png`. `/cards/<id>/qr.png` returns `image/png` with `Cache-Control: no-store`. `/cards/<id>/vcard.vcf` returns `text/vcard; charset=utf-8` with an attachment filename derived from the card display name.
```

with:

```markdown
HTML routes return Django-rendered HTML. `/cards/<id>/qr/fullscreen/` returns a mobile-first presentation HTML page containing the card display name and an image that references `/cards/<id>/qr.png`. `/cards/<id>/qr.png` returns `image/png` with `Cache-Control: no-store`. `/cards/<id>/vcard.vcf` returns `text/vcard; charset=utf-8` with an attachment filename derived from the card display name.
```

- [ ] **Step 2: Update card feature docs**

In `docs/features/cards.md`, replace this paragraph:

```markdown
The fullscreen QR page at `/cards/<id>/qr/fullscreen/` shows the card name and a large QR code in a focused layout. It is linked from the card detail page and is intended for presenting a card from a phone, tablet, or display while keeping the normal detail page available for editing and downloads.
```

with:

```markdown
The fullscreen QR page at `/cards/<id>/qr/fullscreen/` shows the card name and a large QR code in a mobile-first presentation layout. It is linked from the card detail page and is intended for presenting a card from a phone, tablet, or display while keeping the normal detail page available for editing and downloads.
```

- [ ] **Step 3: Add a changelog entry**

Add this entry at the top of `docs/CHANGELOG.md`, immediately after `# Changelog`:

```markdown
## 2026-06-05 — Improve fullscreen QR presentation
- Improve the fullscreen QR page with mobile-safe viewport sizing and a polished presentation-display layout.

```

- [ ] **Step 4: Review the documentation diff**

Run:

```bash
git diff -- API.md docs/features/cards.md docs/CHANGELOG.md
```

Expected: diff shows only the API wording, card feature wording, and changelog entry described in this task.

- [ ] **Step 5: Commit the documentation**

Run:

```bash
git add API.md docs/features/cards.md docs/CHANGELOG.md
git commit -m "docs: update fullscreen QR presentation notes"
```

Expected: commit succeeds with the documentation update.

---

### Task 3: Verify Fullscreen QR Fits Mobile

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

- [ ] **Step 4: Perform mobile visual QA**

Start the local Django server:

```bash
python manage.py runserver 127.0.0.1:8000
```

In the in-app Browser or another browser, load a card's fullscreen QR page at a mobile viewport around `390x844`.

Expected visual result:

```text
- The page fits the mobile viewport without vertical scrolling for normal names.
- The card name is visible and does not overlap the controls or QR code.
- The QR code remains square, centered, and large enough to scan.
- Back and Download controls remain visible but visually secondary.
```

- [ ] **Step 5: Inspect the final diff**

Run:

```bash
git status --short
git diff --check
```

Expected: `git diff --check` prints no whitespace errors. `git status --short` is empty if the previous task commits were created successfully.

- [ ] **Step 6: Report verification**

Post a concise summary with:

```text
Verification complete:
- cards tests: pass
- full Django tests: pass
- route resolution: /cards/1/qr/fullscreen/
- mobile visual QA: pass
- whitespace check: pass
```
