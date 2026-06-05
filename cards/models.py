from django.conf import settings
from django.db import models
from django.urls import reverse


def _vcard_escape(value):
    """Escape a value for inclusion in a vCard field (RFC 6350 / 2426)."""
    return (
        (value or "")
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(",", "\\,")
        .replace(";", "\\;")
    )


class BusinessCard(models.Model):
    """A virtual contact / business card owned by a user.

    A single user can own many cards (work, freelance, personal, ...).
    Each card can be rendered to a vCard string and a scannable QR code.
    """

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cards",
    )
    label = models.CharField(
        max_length=80,
        blank=True,
        help_text="A name for this card, e.g. 'Work' or 'Freelance'.",
    )
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    email = models.EmailField(blank=True)
    organization = models.CharField(max_length=120, blank=True)
    title = models.CharField(max_length=120, blank=True)
    website = models.URLField(max_length=300, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.full_label

    @property
    def display_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def full_label(self):
        return self.label or self.display_name or f"Untitled card #{self.pk or '—'}"

    @property
    def role_line(self):
        return " · ".join(p for p in (self.title, self.organization) if p)

    @property
    def normalized_website(self):
        url = self.website.strip()
        if url and not url.lower().startswith(("http://", "https://")):
            return "https://" + url
        return url

    def get_absolute_url(self):
        return reverse("cards:detail", args=[self.pk])

    def to_vcard(self):
        """Return this card serialised as a vCard 3.0 string."""
        e = _vcard_escape
        lines = ["BEGIN:VCARD", "VERSION:3.0"]
        lines.append(f"N:{e(self.last_name)};{e(self.first_name)};;;")
        fn = self.display_name or self.phone or self.email or "Contact"
        lines.append(f"FN:{e(fn)}")
        if self.organization:
            lines.append(f"ORG:{e(self.organization)}")
        if self.title:
            lines.append(f"TITLE:{e(self.title)}")
        if self.phone:
            lines.append(f"TEL;TYPE=CELL:{e(self.phone)}")
        if self.email:
            lines.append(f"EMAIL;TYPE=INTERNET:{e(self.email)}")
        if self.normalized_website:
            lines.append(f"URL:{e(self.normalized_website)}")
        lines.append("END:VCARD")
        return "\r\n".join(lines)
