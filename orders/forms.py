from django import forms


class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(
        label="Delivery address",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Enter your complete delivery address"}),
    )
