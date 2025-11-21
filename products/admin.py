# products/admin.py

from django.contrib import admin
# YENİ: Color ve Size modellerini import et
from .models import (
    Category, Product, ProductVariant, ProductImage, 
    Color, Size, Review
)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    # ... (Mevcut CategoryAdmin ayarlarınız) ...
    list_display = ['name', 'slug', 'parent', 'order', 'icon_class'] 
    list_editable = ['order', 'icon_class'] 
    list_filter = ('parent',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# ==================================================
# === YENİ ADMIN MODELLERİ ===
# ==================================================
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name', 'hex_code')
    search_fields = ('name',)

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
# ==================================================

# ... (ProductVariantInline, ProductImageInline, ProductAdmin ayarlarınızda değişiklik yok) ...

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1 

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    # YENİ: Admin panelinde renk seçimi görünsün
    fields = ('image', 'color', 'alt_text')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # YENİ: 'category' yerine 'get_primary_category' gösterelim
    list_display = ['name', 'get_primary_category', 'created_at']
    # YENİ: 'secondary_categories' eklendi
    list_filter = ['category', 'secondary_categories', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline]
    
    # ============================================
    # === GÜNCELLEME: filter_horizontal ===
    # ============================================
    # ManyToMany alanlarını daha kullanışlı hale getirir
    filter_horizontal = ('secondary_categories', 'favourited_by',)
    # ============================================
    
    # YENİ: list_display için yardımcı fonksiyon
    @admin.display(description='Ana Kategori', ordering='category')
    def get_primary_category(self, obj):
        return obj.category

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    # GÜNCELLENDİ: İlişkili alanlara göre arama/filtreleme
    list_display = ('product', 'size', 'color', 'sku', 'price', 'stock')
    list_filter = ('size', 'color', 'product__category') # product__name yerine product__category daha mantıklı olabilir
    search_fields = ('sku', 'product__name', 'size__name', 'color__name')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'created_at', 'id')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    # Yorum metnini detayda göster, listede değil
    readonly_fields = ('user', 'product', 'created_at')