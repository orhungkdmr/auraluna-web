from django.db import models
from django.utils.text import slugify
from django.core.files.storage import default_storage
from django.conf import settings
import os

# YENİ: DecimalField için
from decimal import Decimal

class SiteSetting(models.Model):
    instagram_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="Instagram URL")

    # ============================================
    # === YENİ KARGO AYARLARI ===
    # ============================================
    shipping_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('49.99'), 
        verbose_name="Sabit Kargo Ücreti"
    )
    free_shipping_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('500.00'), 
        verbose_name="Ücretsiz Kargo Limiti (Bu tutar ve üzeri)"
    )
    # ============================================
    
    class Meta:
        verbose_name = "Site Ayarı"
        verbose_name_plural = "Site Ayarları"

    def __str__(self):
        return "Genel Site Ayarları"


class AnnouncementBanner(models.Model):
    message = models.CharField(max_length=255, verbose_name="Duyuru Metni")
    link = models.URLField(max_length=255, blank=True, null=True, verbose_name="Duyuru Linki (İsteğe bağlı)")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")

    class Meta:
        verbose_name = "Duyuru Bandı"
        verbose_name_plural = "Duyuru Bantları"
        ordering = ['order']

    def __str__(self):
        return self.message


class Slide(models.Model):
    SLIDE_TYPES = (
        ('image', 'Resim'),
        ('video', 'Video'),
    )
    
    title = models.CharField(max_length=100, verbose_name="Başlık")
    subtitle = models.CharField(max_length=200, blank=True, null=True, verbose_name="Alt Başlık")
    button_text = models.CharField(max_length=50, verbose_name="Buton Metni")
    button_link = models.CharField(max_length=255, verbose_name="Buton Linki")
    
    slide_type = models.CharField(max_length=10, choices=SLIDE_TYPES, default='image', verbose_name="Slayt Tipi")
    
    image = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Resim (Resim tipi veya Video kapağı)")
    video = models.FileField(upload_to='slides/videos/', blank=True, null=True, verbose_name="Video (Video tipi)")
    
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Slayt"
        verbose_name_plural = "Slaytlar"
        ordering = ['order']

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        # Eğer video varsa ve video tipi seçiliyse, resim alanını (eğer varsa) temizle
        # GÜNCELLEME: Hayır, temizleme. Resim alanı video kapak resmi (poster) olarak kullanılabilir.
        # if self.slide_type == 'video' and self.video:
        #     if self.image:
        #         self.image = None # Resim alanını temizle

        # Eğer resim varsa ve resim tipi seçiliyse, video alanını temizle
        if self.slide_type == 'image' and self.image:
            if self.video:
                # Eski videoyu depolamadan sil
                if self.pk:
                    try:
                        old_instance = Slide.objects.get(pk=self.pk)
                        if old_instance.video and old_instance.video.name != self.video.name:
                            default_storage.delete(old_instance.video.name)
                    except Slide.DoesNotExist:
                        pass # Yeni nesne, eski video yok
                self.video = None # Video alanını temizle

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # İlişkili dosyaları depolamadan sil
        if self.image:
            default_storage.delete(self.image.name)
        if self.video:
            default_storage.delete(self.video.name)
        super().delete(*args, **kwargs)