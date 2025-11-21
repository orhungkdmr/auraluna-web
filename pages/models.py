from django.db import models
from django.core.exceptions import ValidationError

class SiteSetting(models.Model):
    """
    Site genelindeki ayarları (kargo ücreti, sosyal medya vb.) yönetmek için model.
    Genellikle sadece 1 kayıt tutulur.
    """
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Kargo Ücreti")
    free_shipping_threshold = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Ücretsiz Kargo Limiti")
    
    # İletişim Bilgileri
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Telefon Numarası")
    email_address = models.EmailField(blank=True, null=True, verbose_name="E-posta Adresi")
    address = models.TextField(blank=True, null=True, verbose_name="Adres")
    
    # Sosyal Medya
    instagram_url = models.URLField(blank=True, null=True, verbose_name="Instagram Linki")
    facebook_url = models.URLField(blank=True, null=True, verbose_name="Facebook Linki")
    twitter_url = models.URLField(blank=True, null=True, verbose_name="Twitter/X Linki")

    def __str__(self):
        return "Site Ayarları"

    class Meta:
        verbose_name = "Site Ayarı"
        verbose_name_plural = "Site Ayarları"


class AnnouncementBanner(models.Model):
    """
    Sayfanın en üstündeki kayan duyuru bandı.
    """
    message = models.CharField(max_length=255, verbose_name="Duyuru Mesajı")
    link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Link (Opsiyonel)", help_text="Tıklandığında gidilecek adres")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")

    class Meta:
        ordering = ('order',)
        verbose_name = "Duyuru Bandı"
        verbose_name_plural = "Duyuru Bantları"

    def __str__(self):
        return self.message


class HeroSlide(models.Model):
    """
    Ana sayfa slider (karusel) yönetimi.
    """
    SLIDE_TYPE_CHOICES = (
        ('image', 'Resim'),
        ('video', 'Video'),
    )
    slide_type = models.CharField(
        max_length=10, 
        choices=SLIDE_TYPE_CHOICES, 
        default='image',
        verbose_name="Slayt Türü"
    )

    # Medya Alanları
    image = models.ImageField(
        upload_to='hero_slides/', 
        blank=True, 
        null=True, 
        verbose_name="Slayt Resmi"
    )
    video = models.FileField(
        upload_to='hero_videos/', 
        blank=True, 
        null=True, 
        verbose_name="Slayt Videosu (MP4)",
        help_text="Eğer video seçerseniz resim yerine video oynatılır."
    )

    # --- GÜNCELLENEN ALANLAR (OPSİYONEL YAPILDI) ---
    title = models.CharField(
        max_length=200, 
        blank=True,  # Zorunlu değil
        null=True,   # Boş olabilir
        verbose_name="Başlık"
    )
    subtitle = models.TextField(
        blank=True,  # Zorunlu değil
        null=True,   # Boş olabilir
        verbose_name="Alt Başlık"
    )
    
    # Buton/Link Alanları
    button_text = models.CharField(
        max_length=50, 
        blank=True,  # Zorunlu değil (Tasarımda kaldırılsa bile veritabanı hatası vermemesi için)
        null=True, 
        verbose_name="Buton Yazısı"
    )
    button_link = models.CharField(
        max_length=200, 
        blank=True, 
        null=True, 
        verbose_name="Yönlendirilecek Link (URL)",
        help_text="Slayta tıklandığında gidilecek adres (örn: /products/erkek/)"
    )
    
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        ordering = ('order',)
        verbose_name = "Ana Sayfa Slaytı"
        verbose_name_plural = "Ana Sayfa Slaytları"

    def clean(self):
        # Resim veya Video'dan en az birinin seçili olmasını zorunlu kılmak için
        if self.slide_type == 'image' and not self.image:
            raise ValidationError("Resim türünü seçtiyseniz bir resim yüklemelisiniz.")
        if self.slide_type == 'video' and not self.video:
            raise ValidationError("Video türünü seçtiyseniz bir video yüklemelisiniz.")

    def __str__(self):
        # Başlık yoksa ID ile gösterelim
        return self.title if self.title else f"Slayt #{self.id}"