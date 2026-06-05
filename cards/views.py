import io

import qrcode
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import BusinessCardForm
from .models import BusinessCard


class OwnedCardsMixin(LoginRequiredMixin):
    """Restrict every queryset to cards owned by the current user."""

    model = BusinessCard

    def get_queryset(self):
        return BusinessCard.objects.filter(owner=self.request.user)


class CardListView(OwnedCardsMixin, ListView):
    template_name = "cards/card_list.html"
    context_object_name = "cards"


class CardDetailView(OwnedCardsMixin, DetailView):
    template_name = "cards/card_detail.html"
    context_object_name = "card"


class CardQRFullscreenView(OwnedCardsMixin, DetailView):
    template_name = "cards/card_qr_fullscreen.html"
    context_object_name = "card"


class CardCreateView(LoginRequiredMixin, CreateView):
    model = BusinessCard
    form_class = BusinessCardForm
    template_name = "cards/card_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_create"] = True
        return ctx


class CardUpdateView(OwnedCardsMixin, UpdateView):
    form_class = BusinessCardForm
    template_name = "cards/card_form.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["is_create"] = False
        return ctx


class CardDeleteView(OwnedCardsMixin, DeleteView):
    template_name = "cards/card_confirm_delete.html"
    success_url = reverse_lazy("cards:list")
    context_object_name = "card"


def _owned_card_or_404(request, pk):
    if not request.user.is_authenticated:
        raise Http404("Not found.")
    return get_object_or_404(BusinessCard, pk=pk, owner=request.user)


def card_qr_png(request, pk):
    """Render the card's vCard as a PNG QR code."""
    card = _owned_card_or_404(request, pk)
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(card.to_vcard())
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1b1712", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    response = HttpResponse(buffer.getvalue(), content_type="image/png")
    response["Cache-Control"] = "no-store"
    return response


def card_vcf(request, pk):
    """Download the card as a .vcf file."""
    card = _owned_card_or_404(request, pk)
    response = HttpResponse(card.to_vcard(), content_type="text/vcard; charset=utf-8")
    base = (card.display_name or card.label or "contact").strip().replace(" ", "_")
    response["Content-Disposition"] = f'attachment; filename="{base or "contact"}.vcf"'
    return response
