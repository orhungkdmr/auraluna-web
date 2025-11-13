from django.contrib import admin
from .models import SiteSetting, AnnouncementBanner, Slide
from django.utils.html import format_html

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    # Kargo alanları eklendi
    list_display = ('__str__', 'instagram_url', 'shipping_fee', 'free_shipping_threshold')
    list_editable = ('instagram_url', 'shipping_fee', 'free_shipping_threshold')

@admin.register(AnnouncementBanner)
class AnnouncementBannerAdmin(admin.ModelAdmin):
    list_display = ('message', 'link', 'is_active', 'order')
    list_editable = ('link', 'is_active', 'order')
    list_display_links = ('message',)

@admin.register(Slide)
class SlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'slide_type', 'image_preview', 'video_preview', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('slide_type', 'is_active')
    search_fields = ('title', 'subtitle')
    
    # Alanları gruplama
    fieldsets = (
        (None, {
            'fields': ('title', 'subtitle', 'button_text', 'button_link', 'is_active', 'order')
        }),
        ('Slayt İçeriği (Lütfen sadece birini seçin)', {
            'fields': ('slide_type', 'image', 'video'),
            'description': "Eğer 'Video' seçerseniz, 'Resim' alanı kapak fotoğrafı olarak kullanılabilir.",
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 100px;" />', obj.image.url)
        return "Resim Yok"
    image_preview.short_description = "Resim Önizleme"

    def video_preview(self, obj):
        if obj.video:
            return format_html('<a href="{}" target="_blank">Videoyu Gör</a>', obj.video.url)
        return "Video Yok"
    video_preview.short_description = "Video"