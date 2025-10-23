# events/forms.py
from django import forms
from .models import PackageBooking

class PackageBookingForm(forms.ModelForm):
    class Meta:
        model = PackageBooking
        fields = ['scheduled_datetime']
        widgets = {
            # Widget HTML5 'datetime-local'
            'scheduled_datetime': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            )
        }