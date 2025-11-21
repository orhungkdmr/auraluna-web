from django.shortcuts import render
from products.models import Product
# DÜZELTME BURADA: Slide yerine HeroSlide import edildi
from .models import HeroSlide, SiteSetting 

def home_view(request):
    # DÜZELTME BURADA: HeroSlide modelini kullanıyoruz
    # Sadece aktif olan slaytları, sıraya göre çekiyoruz
    slides = HeroSlide.objects.filter(is_active=True).order_by('order')
    
    # Ana sayfadaki "Yeni Ürünler" slider'ı için son 8 ürünü çekiyoruz
    new_products = Product.objects.filter(variants__isnull=False).distinct().order_by('-created_at')[:8]
    
    context = {
        'slides': slides,
        'new_products': new_products,
    }
    return render(request, 'pages/home.html', context)

def about_view(request):
    return render(request, 'pages/about.html')

def contact_view(request):
    return render(request, 'pages/contact.html')

def privacy_view(request):
    return render(request, 'pages/privacy.html')