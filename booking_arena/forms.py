# File: booking_arena/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Arena, ArenaOpeningHours

class ArenaForm(forms.ModelForm):
    class Meta:
        model = Arena
        fields = ['name', 'description', 'capacity', 'location', 'img_url', 'google_maps_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500', 
                'placeholder': 'Nama Arena Keren'
            }),
            'description': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500',
                'placeholder': 'Deskripsi singkat...'
            }),
            'capacity': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500'
            }),
            'location': forms.TextInput(attrs={
                 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500'
            }),
             'img_url': forms.URLInput(attrs={
                 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500',
                 'placeholder': 'https://url-gambar.com/arena.jpg'
            }),
            'google_maps_url': forms.URLInput(attrs={
                 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500',
                 'placeholder': 'https://maps.app.goo.gl/...'
            }),
        }


class ArenaOpeningHoursForm(forms.ModelForm):
    class Meta:
        model = ArenaOpeningHours
        fields = ['day', 'open_time', 'close_time']
        widgets = {
            'open_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'close_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control form-control-sm'}),
            'day': forms.HiddenInput(),
        }

ArenaOpeningHoursFormSet = inlineformset_factory(
    Arena, 
    ArenaOpeningHours,
    form=ArenaOpeningHoursForm,
    extra=7, 
    max_num=7,
    validate_max=True,
    can_delete=False,
    can_order=False,
)