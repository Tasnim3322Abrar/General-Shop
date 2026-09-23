from django import forms
from .models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = (
            "full_name",
            "phone",
            "address_line",
            "city",
            "postal_code",
            "is_default",
        )
        widgets = {
            "full_name": forms.TextInput(
                attrs={"placeholder": "Full name"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Phone number"}
            ),
            "address_line": forms.Textarea(
                attrs={
                    "placeholder": "House, road, area",
                    "rows": 3,
                }
            ),
            "city": forms.TextInput(
                attrs={"placeholder": "City"}
            ),
            "postal_code": forms.TextInput(
                attrs={"placeholder": "Postal code"}
            ),
            "is_default": forms.CheckboxInput(),
        }