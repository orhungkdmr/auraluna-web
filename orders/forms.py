from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    # ... (Mevcut OrderCreateForm kodunuz) ...
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

class OrderTrackingForm(forms.Form):
    # ... (Mevcut OrderTrackingForm kodunuz) ...
    order_id = forms.CharField(label='Sipariş Numarası',
                               widget=forms.TextInput(attrs={'placeholder': '#12345'}))
    email = forms.EmailField(label='E-posta Adresi',
                             widget=forms.EmailInput(attrs={'placeholder': 'eposta@adresiniz.com'}))

# ==================================================
# === YENİ KUPON UYGULAMA FORMU ===
# ==================================================
class CouponApplyForm(forms.Form):
    code = forms.CharField(label="Kupon Kodu",
                           widget=forms.TextInput(attrs={
                               'placeholder': 'Kodunuzu girin',
                               'class': 'form-control' # Bootstrap 5 sınıfı
                           }))