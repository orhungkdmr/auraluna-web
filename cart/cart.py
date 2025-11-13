from decimal import Decimal
from django.conf import settings
from products.models import Product, ProductVariant
from orders.models import Coupon
# YENİ: SiteSetting modelini import et
from pages.models import SiteSetting 

class Cart:
    def __init__(self, request):
        """
        Sepeti başlatır ve kuponu/kargo ayarlarını session'dan alır.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart
        
        self.coupon_id = self.session.get('coupon_id')

        # ============================================
        # === YENİ: Kargo ayarlarını yükle ===
        # ============================================
        try:
            # first() yerine [0] kullanmak ve cachingleme yapmak daha iyi olabilir,
            # ama en basit yöntem .first()
            self.site_settings = SiteSetting.objects.first()
        except SiteSetting.DoesNotExist:
            self.site_settings = None
        # ============================================

    def add(self, variant, quantity=1, override_quantity=False):
        """
        Ürün VARYASYONUNU sepete ekler veya miktarını günceller.
        """
        variant_id = str(variant.id)
        if variant_id not in self.cart:
            self.cart[variant_id] = {'quantity': 0, 'price': str(variant.price)}
        
        if override_quantity:
            self.cart[variant_id]['quantity'] = quantity
        else:
            self.cart[variant_id]['quantity'] += quantity
        self.save()

    def save(self):
        # session'ı "modified" olarak işaretle, kaydedildiğinden emin ol
        self.session.modified = True

    def remove(self, variant):
        """
        Varyasyonu sepetten siler.
        """
        variant_id = str(variant.id)
        if variant_id in self.cart:
            del self.cart[variant_id]
            self.save()

    def __iter__(self):
        """
        Session'daki veriyi okur, veritabanından nesneleri alır...
        """
        variant_ids = self.cart.keys()
        variants = ProductVariant.objects.filter(id__in=variant_ids).select_related('product', 'size', 'color')
        
        variants_dict = {str(v.id): v for v in variants}

        for variant_id, item_data in self.cart.items():
            yield {
                'quantity': item_data['quantity'],
                'price': Decimal(item_data['price']),
                'variant': variants_dict.get(variant_id),
                'total_price': Decimal(item_data['price']) * item_data['quantity']
            }

    def __len__(self):
        """
        Sepetteki toplam ürün adedini (miktarların toplamını) sayar.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Sepetin (İNDİRİMSİZ) ara toplam maliyetini hesaplar.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        # sepeti session'dan sil
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    @property
    def coupon(self):
        """
        Session'daki coupon_id'ye karşılık gelen Coupon nesnesini alır.
        """
        if self.coupon_id:
            try:
                return Coupon.objects.get(id=self.coupon_id, active=True)
            except Coupon.DoesNotExist:
                self.session['coupon_id'] = None
                self.save()
        return None

    def get_discount(self):
        """
        Kupon varsa, indirim tutarını hesaplar.
        """
        if self.coupon and self.coupon.is_valid():
            total_price = self.get_total_price()
            discount_percentage = self.coupon.discount
            return (Decimal(discount_percentage) / 100) * total_price
        return Decimal(0)

    def get_total_price_after_discount(self):
        """Ara toplamdan indirimi çıkarır (KARGO HARİÇ)."""
        return (self.get_total_price() - self.get_discount()).quantize(Decimal('.01'))

    # ============================================
    # === YENİ KARGO VE GENEL TOPLAM METODLARI ===
    # ============================================
    
    def get_shipping_fee(self):
        """Kargo ücretini hesaplar."""
        if self.site_settings:
            subtotal = self.get_total_price_after_discount()
            if subtotal >= self.site_settings.free_shipping_threshold:
                return Decimal('0.00')
            return self.site_settings.shipping_fee.quantize(Decimal('.01'))
        
        # Ayar yoksa varsayılan olarak ücretsiz yap (güvenli varsayım)
        return Decimal('0.00')

    def get_grand_total(self):
        """Genel Toplam (İndirimli Fiyat + Kargo)."""
        return self.get_total_price_after_discount() + self.get_shipping_fee()
    
    # ============================================