from django.contrib import admin
from .models import Order, OrderItem, Coupon

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # product ve variant alanları sadece okunabilir olsun (değiştirilemesin)
    readonly_fields = ('product', 'variant', 'price', 'quantity', 'get_cost') 
    can_delete = False
    extra = 0
    # get_cost fonksiyonunu admin panelinde göster
    fields = ('product', 'variant', 'price', 'quantity', 'get_cost')

    def get_cost(self, obj):
        return obj.get_cost()
    get_cost.short_description = "Toplam Maliyet"

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # ============================================
    # === GÜNCELLENEN ADMİN GÖRÜNÜMÜ ===
    # ============================================
    list_display = [
        'id', 'user', 'email', 'paid', 
        'status', 'shipping_company', 'tracking_number', # YENİ ALANLAR
        'created_at'
    ]
    # YENİ: Bu alanları listeden hızlıca düzenle
    list_editable = ['paid', 'status', 'shipping_company', 'tracking_number']
    
    # YENİ: Duruma göre filtrele
    list_filter = ['paid', 'status', 'created_at', 'coupon']
    # ============================================
    
    search_fields = ['id', 'first_name', 'last_name', 'email', 'user__username']
    inlines = [OrderItemInline]
    readonly_fields = ('get_total_cost_display',)
    list_select_related = ('user', 'coupon')

    def get_total_cost_display(self, obj):
        return f"{obj.get_total_cost()} TL"
    get_total_cost_display.short_description = "Genel Toplam (Kargo Dahil)"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'valid_from', 'valid_to', 'discount', 'active', 'is_valid_now']
    list_filter = ['active', 'valid_from', 'valid_to']
    search_fields = ['code']
    
    def is_valid_now(self, obj):
        return obj.is_valid()
    is_valid_now.boolean = True 
    is_valid_now.short_description = "Şu an Geçerli mi?"