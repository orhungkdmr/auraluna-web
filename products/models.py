# products/models.py

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify # YENİ: Slugify importu (Size modeli için)

class Category(models.Model):
    # ... (Mevcut Kategori modelinizde değişiklik yok) ...
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    order = models.PositiveIntegerField(default=0, help_text="Gösterim sırası (küçük olan öne gelir)")
    icon_class = models.CharField(max_length=50, blank=True, null=True, verbose_name="İkon Sınıfı", help_text="Bootstrap ikon sınıfı (örn: bi-tags-fill, bi-gem)")
    class Meta:
        ordering = ('order', 'name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    def __str__(self):
        full_path = [self.name]; k = self.parent
        while k is not None: full_path.append(k.name); k = k.parent
        return ' > '.join(full_path[::-1])
    def get_absolute_url(self):
        return reverse('products:product_list_by_category', args=[self.slug])

# ==================================================
# === YENİ MODELLER BURADA BAŞLIYOR ===
# ==================================================

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Renk Adı")
    hex_code = models.CharField(max_length=7, default="#FFFFFF", verbose_name="Hex Kodu", help_text="Örn: #FFFFFF (Beyaz için)")

    class Meta:
        verbose_name = "Renk"
        verbose_name_plural = "Renkler"
    
    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Beden Adı")
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Sıralama (örn: S=1, M=2, L=3)")

    class Meta:
        ordering = ('order', 'name',)
        verbose_name = "Beden"
        verbose_name_plural = "Bedenler"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

# ==================================================
# === YENİ MODELLER BİTİYOR ===
# ==================================================


# ...

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Ana Kategori")
    secondary_categories = models.ManyToManyField(
        Category, 
        related_name='secondary_products', 
        blank=True, 
        verbose_name="İkincil Kategoriler (Etiketler)"
    )
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    
    # GÜNCELLEME: blank=True, null=True eklendi (Zorunluluk kalktı)
    image = models.ImageField(upload_to='products/', null=True, blank=True, help_text="Ana kapak fotoğrafı (Opsiyonel)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favourited_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favourite_products', blank=True)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self): return self.name
    
    def get_absolute_url(self): return reverse('products:product_detail', args=[self.slug])

    # YENİ EKLENEN YARDIMCI FONKSİYON
    @property
    def get_main_image(self):
        """
        Eğer ana resim (image) varsa onu döner.
        Yoksa, galerideki (ProductImage) ilk resmi döner.
        O da yoksa None döner.
        """
        if self.image:
            return self.image
        
        # Galeriden ilk resmi al
        first_gallery_image = self.images.first()
        if first_gallery_image:
            return first_gallery_image.image
            
        return None

    def get_color_variant_data(self):
        """
        Ürün kartı için renk seçeneklerini ve o renge ait resmi hazırlar.
        """
        data = []
        variants = self.variants.select_related('color').all()
        seen_colors = set()
        
        for v in variants:
            if v.color and v.color.id not in seen_colors:
                # 1. Bu renge özel atanmış resim var mı?
                color_image = self.images.filter(color=v.color).first()
                
                # 2. Resim URL'ini belirle
                if color_image:
                    image_url = color_image.image.url
                elif self.image:
                    image_url = self.image.url # Ana resim varsa onu kullan
                else:
                    # Hiçbir resim yoksa placeholder
                    image_url = '/static/images/placeholder.png' 
                
                data.append({
                    'color_id': v.color.id,
                    'color_name': v.color.name,
                    'hex_code': v.color.hex_code,
                    'image_url': image_url
                })
                seen_colors.add(v.color.id)
        return data

        
class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    # YENİ EKLENDİ: Resmi bir renge bağlamak için
    color = models.ForeignKey('Color', on_delete=models.SET_NULL, null=True, blank=True, related_name='product_images', verbose_name="Renk (Opsiyonel)")
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.color.name if self.color else 'Genel'} - {self.id}"
# ==================================================
# === GÜNCELLENEN ProductVariant MODELİ ===
# ==================================================
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    
    sku = models.CharField(max_length=100, unique=True, help_text="Benzersiz Stok Kodu (SKU), örn: AUR-GM-BYZ-M")
    
    # --- DEĞİŞİKLİKLER ---
    # CharField'lar ForeignKey'lere dönüştürüldü
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name='variants', verbose_name="Beden")
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='variants', verbose_name="Renk")
    # --- DEĞİŞİKLİKLER SONU ---
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    
    class Meta:
        # unique_together hala geçerli
        unique_together = ('product', 'size', 'color')
    
    def __str__(self): 
        # İlişkili modellerin adını almak için __str__ güncellendi
        return f'{self.product.name} - {self.size.name} / {self.color.name}'

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Ürün")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="Kullanıcı")
    
    RATING_CHOICES = (
        (1, '1 - Çok Kötü'),
        (2, '2 - Kötü'),
        (3, '3 - Orta'),
        (4, '4 - İyi'),
        (5, '5 - Mükemmel'),
    )
    
    rating = models.PositiveIntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puan"
    )
    comment = models.TextField(verbose_name="Yorum Metni")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Değerlendirme"
        verbose_name_plural = "Değerlendirmeler"
        ordering = ('-created_at',)
        
        # Bir kullanıcı bir ürüne sadece bir kez yorum yapabilmeli
        unique_together = ('product', 'user',) 

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} Puan)"

class StockNotification(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stock_notifications', verbose_name="Varyasyon")
    email = models.EmailField(verbose_name="E-posta Adresi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Talep Tarihi")
    is_notified = models.BooleanField(default=False, verbose_name="Bildirim Gönderildi mi?")

    class Meta:
        verbose_name = "Stok Bildirimi"
        verbose_name_plural = "Stok Bildirimleri"
        ordering = ('-created_at',)

    def __str__(self):
        return f"{self.email} - {self.variant}"