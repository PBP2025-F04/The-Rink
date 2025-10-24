from django import forms
from .models import Arena

class ArenaForm(forms.ModelForm):
    class Meta:
        model = Arena
        fields = ['name', 'description', 'capacity', 'location', 'img_url', 'opening_hours_text']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'opening_hours_text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Senin: 09.00-21.00\nSelasa: ...'}),
        }