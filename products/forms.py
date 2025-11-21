from django import forms
from .models import Review, StockNotification

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Yorumunuzu buraya yazın...'}),
        }
        labels = {
            'rating': 'Puanınız',
            'comment': 'Yorumunuz'
        }

class StockNotificationForm(forms.ModelForm):
    class Meta:
        # DÜZELTME: 'products.StockNotification' değil, direkt sınıf adı
        model = StockNotification 
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta adresiniz'}),
        }