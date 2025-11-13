from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Ana ürün listesi (örn: /products/)
    path('', views.product_list, name='product_list'),
    
    # Hızlı Bakış API'ı (örn: /products/quick-view/keten-gomlek/)
    path('quick-view/<slug:slug>/', views.product_quick_view, name='product_quick_view'),
    
    # Favorilerim sayfası (örn: /products/favourites/)
    path('favourites/', views.favourite_list, name='favourite_list'),
    
    # Favorilere ekleme/çıkarma işlemi (örn: /products/favourite/keten-gomlek/)
    path('favourite/<slug:product_slug>/', views.toggle_favourite, name='toggle_favourite'),
    
    # Kategoriye göre filtrelenmiş ürün listesi (örn: /products/erkek/)
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Ürün detay sayfası (örn: /products/p/keten-gomlek/)
    path('p/<slug:slug>/', views.product_detail, name='product_detail'),
]