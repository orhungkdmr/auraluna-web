from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('quick-view/<slug:slug>/', views.product_quick_view, name='product_quick_view'),
    path('favourites/', views.favourite_list, name='favourite_list'),
    path('favourite/<slug:product_slug>/', views.toggle_favourite, name='toggle_favourite'),
    path('notify-stock/', views.stock_notification_request, name='stock_notification_request'),
    
    # --- BU SATIRIN EKLİ OLDUĞUNDAN EMİN OL ---
    path('live-search/', views.live_search, name='live_search'),
    # -------------------------------------------
    
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('p/<slug:slug>/', views.product_detail, name='product_detail'),
]