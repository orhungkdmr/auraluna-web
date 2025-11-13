from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Tek sayfa checkout akışı
    path('checkout/', views.checkout, name='checkout'), 
    
    # Sipariş geçmişi sayfası
    path('history/', views.order_history, name='order_history'),
    
    # Ödeme süreci adımları
    path('process/', views.payment_process, name='payment_process'),
    path('done/', views.payment_done, name='payment_done'),
    path('canceled/', views.payment_canceled, name='payment_canceled'),

    path('track/', views.order_tracking_view, name='order_tracking'),
]