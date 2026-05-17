from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "you@example.com"}
        ),
    )
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Last Name"}
        ),
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "+998 ..."}
        ),
    )

    class Meta:
        model = CustomUser
        fields = ["email", "first_name", "last_name", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Parol"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Parolni takrorlang"}
        )


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "you@example.com",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Parol"}
        ),
    )

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Incorrect credentials!")
            if not user.is_active:
                raise forms.ValidationError("Account is not active!")
            cleaned["user"] = user
        return cleaned


class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "phone", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.FileInput(attrs={"class": "form-control"}),
        }
