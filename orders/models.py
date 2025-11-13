from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal

class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Kupon Kodu")
    valid_from = models.DateTimeField(verbose_name="Geçerlilik Başlangıcı")
    valid_to = models.DateTimeField(verbose_name="Geçerlilik Bitişi")
    discount = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="İndirim Yüzdesi (%)",
        help_text="Yüzde olarak (örn: 20)"
    )
    active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Kupon"
        verbose_name_plural = "Kuponlar"

    def __str__(self):
        return self.code
        
    def is_valid(self):
        """Kuponun şu anda geçerli olup olmadığını kontrol eder."""
        now = timezone.now()
        return self.active and self.valid_from <= now and self.valid_to >= now

class Order(models.Model):
    
    # ============================================
    # === YENİ SİPARİŞ DURUMU SEÇENEKLERİ ===
    # ============================================
    STATUS_CHOICES = (
        ('pending', 'Ödeme Bekleniyor'),
        ('processing', 'Hazırlanıyor'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('canceled', 'İptal Edildi'),
    )
    # ============================================

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    
    coupon = models.ForeignKey(Coupon,
                               related_name='orders',
                               null=True,
                               blank=True,
                               on_delete=models.SET_NULL,
                               verbose_name="Kullanılan Kupon")
    discount = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    shipping_cost = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=Decimal('0.00'), 
        verbose_name="Kargo Ücreti"
    )
    
    # ============================================
    # === YENİ KARGO TAKİP ALANLARI ===
    # ============================================
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Sipariş Durumu"
    )
    shipping_company = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Kargo Firması"
    )
    tracking_number = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Kargo Takip No"
    )
    # ============================================

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"

    def __str__(self):
        return f'Sipariş #{self.id}'

    # ============================================
    # === GÜNCELLENEN get_total_cost ===
    # ============================================
    def get_total_cost(self):
        """Ürün toplamı, indirim VE kargo dahil nihai fiyatı hesaplar."""
        
        items_total = sum(item.get_cost() for item in self.items.all()) or Decimal('0.00')
        
        if self.discount > 0:
            discount_amount = (Decimal(self.discount) / Decimal('100')) * items_total
            total_before_shipping = (items_total - discount_amount)
        else:
            total_before_shipping = items_total
            
        # Fiyata kargo ücretini ekle
        grand_total = total_before_shipping + self.shipping_cost
        
        return grand_total.quantize(Decimal('.01'))
    # ============================================

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='order_items', on_delete=models.CASCADE)
    variant = models.ForeignKey('products.ProductVariant', related_name='order_items', on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity