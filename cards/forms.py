from django import forms

from .models import BusinessCard


class BusinessCardForm(forms.ModelForm):
    class Meta:
        model = BusinessCard
        fields = [
            "label",
            "first_name",
            "last_name",
            "phone",
            "email",
            "organization",
            "title",
            "website",
        ]
        widgets = {
            "label": forms.TextInput(attrs={"placeholder": "Work, Freelance, Personal…"}),
            "first_name": forms.TextInput(attrs={"placeholder": "Ada", "autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Lovelace", "autocomplete": "family-name"}),
            "phone": forms.TextInput(attrs={"type": "tel", "placeholder": "+1 555 0100", "autocomplete": "tel"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "organization": forms.TextInput(attrs={"placeholder": "Analytical Engines", "autocomplete": "organization"}),
            "title": forms.TextInput(attrs={"placeholder": "Founder", "autocomplete": "organization-title"}),
            "website": forms.TextInput(attrs={"type": "url", "placeholder": "example.com", "autocomplete": "url"}),
        }
