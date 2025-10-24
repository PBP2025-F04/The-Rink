from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, SellerProfile, UserType

class UserTypeForm(forms.ModelForm):
    user_type = forms.ChoiceField(
        choices=UserType.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Tipe Pengguna"
    )

    class Meta:
        model = UserType
        fields = ['user_type']

class CustomUserCreationForm(UserCreationForm):
    user_type = forms.ChoiceField(
        choices=UserType.USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Tipe Pengguna"
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'user_type']

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'full_name', 'phone_number', 'email', 'date_of_birth', 'address']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['business_name', 'phone_number', 'email', 'business_address']
