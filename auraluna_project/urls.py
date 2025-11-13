# auraluna_project/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# i18n eklediyseniz: from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    # Dil URL'si (varsa): path('i18n/', include('django.conf.urls.i18n')),

    # Uygulama URL'leri (i18n kullanıyorsanız i18n_patterns içinde olmalı)
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),

    # --- ACCOUNTS URL'LERİ ---
    # Django'nun hazır auth URL'lerini (login, logout, password_change VE password_reset dahil) ekleyin
    path('accounts/', include('django.contrib.auth.urls')),
    # Kendi signup ve profil URL'lerinizi ekleyin
    path('accounts/', include('accounts.urls')),
    # --- ACCOUNTS URL'LERİ SONU ---

    path('', include('pages.urls')),
    path('products/', include('products.urls')),
]

# Medya dosyaları
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Not: Eğer i18n_patterns kullanıyorsanız, uygulama URL'lerini (cart, orders, accounts, pages, products)
# i18n_patterns içine taşıdığınızdan emin olun. django.contrib.auth.urls genellikle dil bağımsızdır
# ve ana urlpatterns içinde kalabilir.