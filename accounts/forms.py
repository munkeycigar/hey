from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "you@example.com"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
