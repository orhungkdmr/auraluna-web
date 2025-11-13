# accounts/urls.py

from django.urls import path
# YENİ: Django'nun hazır auth görünümlerini ve kendi view'larımızı import edelim
from django.contrib.auth import views as auth_views 
from .views import SignUpView, account_profile_view, account_update_view # Yeni view'ları import et

app_name = 'accounts'

urlpatterns = [
    # Kayıt olma sayfası
    path("signup/", SignUpView.as_view(), name="signup"),

    # YENİ: Hesap Bilgileri (Profil) Sayfası
    path("profile/", account_profile_view, name="account_profile"),

    # YENİ: Hesap Bilgilerini Güncelleme Sayfası
    path("profile/update/", account_update_view, name="account_update"),

    # YENİ: Şifre Değiştirme Sayfası (Django'nun hazır view'ı)
    path("password_change/", 
         auth_views.PasswordChangeView.as_view(
             template_name='registration/password_change_form.html', # Kullanılacak şablon
             success_url='password_change_done' # Başarılı olunca yönlendirilecek URL adı
         ), 
         name="password_change"),

    # YENİ: Şifre Değiştirme Başarılı Sayfası (Django'nun hazır view'ı)
    path("password_change/done/", 
         auth_views.PasswordChangeDoneView.as_view(
             template_name='registration/password_change_done.html' # Kullanılacak şablon
         ), 
         name="password_change_done"),
]