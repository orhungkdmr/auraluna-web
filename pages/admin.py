from django.contrib import admin
from .models import SiteSetting, AnnouncementBanner, HeroSlide

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'shipping_fee', 'free_shipping_threshold')
    # Site ayarları genellikle tek bir kayıt olduğu için ekleme/silme işlemlerini kısıtlayabilirsin (opsiyonel)
    def has_add_permission(self, request):
        # Eğer zaten bir kayıt varsa yenisine izin verme
        if self.model.objects.exists():
            return False
        return True

@admin.register(AnnouncementBanner)
class AnnouncementBannerAdmin(admin.ModelAdmin):
    list_display = ('message', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active',)

@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title_or_id', 'slide_type', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'slide_type')
    ordering = ('order',)
    
    # Başlık opsiyonel olduğu için listede boş görünmesin diye özel fonksiyon
    def title_or_id(self, obj):
        return obj.title if obj.title else f"Slayt #{obj.id}"
    title_or_id.short_description = "Başlık"