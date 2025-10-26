from django import forms
from django.contrib.auth.models import User
from .models import CartItem, Rental, Gear

class GearForm(forms.ModelForm):
    seller = forms.ModelChoiceField(
        queryset=None,
        required=False,
        empty_label="Created by Admin",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Gear
        fields = ['name', 'category', 'price_per_day', 'image_url', 'description', 'stock', 'seller']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'price_per_day': forms.NumberInput(attrs={'class': 'form-control'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from authentication.models import UserType
        # Only show seller users for admin selection
        seller_users = UserType.objects.filter(user_type='seller').values_list('user', flat=True)
        self.fields['seller'].queryset = User.objects.filter(id__in=seller_users)

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
