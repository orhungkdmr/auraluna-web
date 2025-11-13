# pages/views.py dosyasına ekleyin (eğer yoksa)

from django.shortcuts import render
from products.models import Product
from .models import Slide, SiteSetting # SiteSetting'i de import ettiğinizden emin olun (önceki adım için)

def home_view(request):
    """
    Ana sayfayı oluşturur. Veritabanından en yeni ürünleri ve
    ana sayfa karuseli için slaytları çeker.
    """
    new_products = Product.objects.filter(variants__isnull=False).distinct().order_by('-created_at')[:8]
    slides = Slide.objects.all()
    context = {
        'new_products': new_products,
        'slides': slides,
    }
    return render(request, 'pages/home.html', context)

def about_view(request):
    """
    Hakkımızda sayfasını gösterir.
    """
    return render(request, 'pages/about.html')

def contact_view(request):
    """
    İletişim sayfasını gösterir.
    """
    return render(request, 'pages/contact.html')

# YENİ/KONTROL EDİLMESİ GEREKEN: Gizlilik Politikası View'ı
def privacy_view(request):
    """
    Gizlilik Politikası sayfasını gösterir.
    """
    return render(request, 'pages/privacy.html')