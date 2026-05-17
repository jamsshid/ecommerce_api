from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            "full_name",
            "email",
            "phone",
            "shipping_address",
            "city",
            "postal_code",
            "notes",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "+1 ..."}
            ),
            "shipping_address": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(
                attrs={"class": "form-control", "rows": 2, "placeholder": "Optional"}
            ),
        }
