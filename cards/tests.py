from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import BusinessCard

User = get_user_model()

PW = "An3xampleP@ss"


class CardFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("ada", password=PW)

    def test_list_requires_login(self):
        resp = self.client.get(reverse("cards:list"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp.url)

    def test_create_card_attaches_owner(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("cards:create"),
            {
                "label": "Work",
                "first_name": "Ada",
                "last_name": "Lovelace",
                "phone": "+1 555 0100",
                "email": "ada@example.com",
                "organization": "Analytical Engines",
                "title": "Founder",
                "website": "example.com",
            },
        )
        self.assertEqual(resp.status_code, 302)
        card = BusinessCard.objects.get()
        self.assertEqual(card.owner, self.user)
        self.assertEqual(card.display_name, "Ada Lovelace")

    def test_user_can_have_multiple_cards(self):
        self.client.force_login(self.user)
        BusinessCard.objects.create(owner=self.user, label="Work", first_name="Ada")
        BusinessCard.objects.create(owner=self.user, label="Personal", first_name="Ada")
        self.assertEqual(self.user.cards.count(), 2)
        resp = self.client.get(reverse("cards:list"))
        self.assertContains(resp, "Work")
        self.assertContains(resp, "Personal")

    def test_qr_png_and_vcf(self):
        self.client.force_login(self.user)
        card = BusinessCard.objects.create(
            owner=self.user, first_name="Ada", last_name="Lovelace", email="ada@example.com"
        )
        qr = self.client.get(reverse("cards:qr", args=[card.pk]))
        self.assertEqual(qr.status_code, 200)
        self.assertEqual(qr["Content-Type"], "image/png")
        self.assertTrue(qr.content.startswith(b"\x89PNG"))

        vcf = self.client.get(reverse("cards:vcf", args=[card.pk]))
        self.assertEqual(vcf.status_code, 200)
        self.assertIn("text/vcard", vcf["Content-Type"])
        body = vcf.content.decode()
        self.assertIn("BEGIN:VCARD", body)
        self.assertIn("FN:Ada Lovelace", body)
        self.assertIn("EMAIL;TYPE=INTERNET:ada@example.com", body)

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

    def test_owner_isolation(self):
        other = User.objects.create_user("charles", password=PW)
        card = BusinessCard.objects.create(owner=other, first_name="Charles", last_name="Babbage")
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("cards:detail", args=[card.pk])).status_code, 404)
        self.assertEqual(self.client.get(reverse("cards:qr", args=[card.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("cards:list")), "Babbage")

    def test_register_logs_user_in(self):
        resp = self.client.post(
            reverse("accounts:register"),
            {
                "username": "grace",
                "email": "grace@example.com",
                "password1": "An3xampleP@ss42",
                "password2": "An3xampleP@ss42",
            },
        )
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="grace").exists())


class VCardSerializationTests(TestCase):
    def test_special_characters_are_escaped(self):
        u = User.objects.create_user("eve", password=PW)
        card = BusinessCard.objects.create(
            owner=u, first_name="A,B", last_name="C;D", organization="X\\Y"
        )
        v = card.to_vcard()
        self.assertIn("N:C\\;D;A\\,B;;;", v)
        self.assertIn("ORG:X\\\\Y", v)
