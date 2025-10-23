from django import forms
from .models import CartItem, Rental

class AddToCartForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1)
    days = forms.IntegerField(min_value=1, max_value=30, initial=1)

    class Meta:
        model = CartItem
        fields = ['quantity', 'days']

    def clean_quantity(self):
        quantity = self.cleaned_data['quantity']
        if quantity < 1:
            raise forms.ValidationError("Quantity harus minimal 1")
        return quantity

    def clean_days(self):
        days = self.cleaned_data['days']
        if not 1 <= days <= 30:
            raise forms.ValidationError("Durasi rental harus antara 1-30 hari")
        return days

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['customer_name']
        widgets = {
            'customer_name': forms.TextInput(attrs={'readonly': 'readonly'})
        }