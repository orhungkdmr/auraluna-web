from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # Sadece bu iki alanı kullanıcıdan alacağız
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Yorumunuzu buraya yazın...'}),
        }
        labels = {
            'rating': 'Puanınız',
            'comment': 'Yorumunuz'
        }