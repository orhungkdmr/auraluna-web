# pages/urls.py
from django.urls import path
# YENİ: privacy_view'ı import et
from .views import home_view, about_view, contact_view, privacy_view 

app_name = 'pages'

urlpatterns = [
    path('', home_view, name='home'),
    path('about/', about_view, name='about'),
    path('contact/', contact_view, name='contact'),
    # YENİ: Gizlilik Politikası URL'si
    path('privacy/', privacy_view, name='privacy'), 
]