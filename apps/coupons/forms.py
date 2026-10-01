from django import forms


class CouponApplyForm(forms.Form):

    code = forms.CharField(
        max_length=50,
        strip=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter coupon code",
                "autocomplete": "off",
            }
        ),
    )