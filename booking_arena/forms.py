from django import forms
from .models import Arena

class ArenaForm(forms.ModelForm):
    class Meta:
        model = Arena
        fields = ['name', 'description', 'capacity', 'location', 'img_url', 'opening_hours_text']
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
                 'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500'
            }),
            'opening_hours_text': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'w-full p-2 border border-gray-300 rounded-md focus:ring-sky-500 focus:border-sky-500',
                'placeholder': 'Senin: 09.00-21.00\nSelasa: ...'
            }),
        }