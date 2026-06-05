from django.urls import path

from . import views

app_name = "cards"

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
