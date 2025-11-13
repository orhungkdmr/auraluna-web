# accounts/forms.py

from django import forms
from django.contrib.auth.models import User
from .models import UserProfile # UserProfile import et

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        help_texts = {'email': 'Lütfen geçerli bir e-posta adresi giriniz.',}

# YENİ: UserProfile için Güncellenmiş Form
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        # YENİ: Alanları güncelle (profile_picture eklendi, address detaylandırıldı)
        fields = ['profile_picture', 'phone_number', 'city', 'district', 'postal_code', 'address_detail']
        widgets = {
            # Açık adres alanını daha büyük yapmak için
            'address_detail': forms.Textarea(attrs={'rows': 3}),
        }
