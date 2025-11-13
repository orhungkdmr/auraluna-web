from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from decimal import Decimal

from products.models import Product, Category, Color, Size, ProductVariant
from orders.models import Coupon
from django.utils import timezone

class CartLogicTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """
        Tüm testlerin kullanacağı verileri bir kez oluşturur.
        (Client buradan taşındı)
        """
        cls.category = Category.objects.create(name="Test Kategori", slug="test-kategori")
        cls.color = Color.objects.create(name="Test Renk", hex_code="#FFF")
        cls.size = Size.objects.create(name="Test Beden", slug="test-beden", order=1)
        
        cls.product = Product.objects.create(
            category=cls.category,
            name="Test Gömlek",
            slug="test-gomlek"
        )
        
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=cls.color,
            size=cls.size,
            sku="TEST-001",
            price=Decimal('100.00'),
            stock=5 
        )
        
        cls.coupon = Coupon.objects.create(
            code="TEST20",
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            discount=20,
            active=True
        )

    # ============================================
    # === GÜNCELLEME BURADA: setUp ===
    # ============================================
    def setUp(self):
        """
        Bu fonksiyon her testten ÖNCE çalışır.
        Her testin temiz bir istemciye (ve oturuma) sahip olmasını sağlar.
        """
        self.client = Client()
    # ============================================

    def test_add_to_cart(self):
        """Test 1: Sepete ürün ekleme ve toplam fiyat kontrolü."""
        
        self.client.post(reverse('cart:cart_add', args=[self.variant.id]), {
            'quantity': 2
        })
        
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart'].get_total_price(), Decimal('200.00'))
        
        print("\nPASSED: Sepete Ekleme Testi")

    def test_stock_limit_on_add(self):
        """Test 2: Stoktan (5) fazla (6) ürün eklemeyi engelleme."""
        
        response = self.client.post(reverse('cart:cart_add', args=[self.variant.id]), {
            'quantity': 6 
        }, follow=True) 
        
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Stok yetersiz.')
        
        self.assertEqual(len(response.context['cart']), 0)
        
        print("PASSED: Stok Sınırı Testi")

    def test_apply_valid_coupon(self):
        """Test 3: Geçerli bir kupon uygulama ve indirim hesaplama."""
        
        # 1. Sepete ürün ekle (follow=True mesajı tüketir)
        self.client.post(reverse('cart:cart_add', args=[self.variant.id]), 
                         {'quantity': 2}, 
                         follow=True)
        
        # 2. Kuponu uygula (follow=True mesajı tüketir)
        self.client.post(reverse('cart:cart_apply_coupon'), 
                         {'code': 'TEST20'}, 
                         follow=True)
        
        # 3. Sepet detay sayfasını son kez çağır ve hesaplamaları kontrol et
        response = self.client.get(reverse('cart:cart_detail'))
        
        cart = response.context['cart']
        
        self.assertEqual(cart.get_total_price(), Decimal('200.00'))
        self.assertEqual(cart.get_discount(), Decimal('40.00'))
        self.assertEqual(cart.get_total_price_after_discount(), Decimal('160.00'))
        
        print("PASSED: Kupon İndirimi Testi")

    def test_apply_invalid_coupon(self):
        """Test 4: Geçersiz kupon kodunu test etme."""
        
        # 1. Sepete ürün ekle (follow=True mesajı tüketir)
        self.client.post(reverse('cart:cart_add', args=[self.variant.id]), 
                         {'quantity': 2}, 
                         follow=True)
            
        # 2. Şimdi geçersiz kuponu uygula (follow=True mesajı tüketir)
        response = self.client.post(reverse('cart:cart_apply_coupon'), 
                                    {'code': 'YOKBOYLEKOD'}, 
                                    follow=True)
        
        # 3. Mesajları kontrol et (Artık taze oturum sayesinde sadece 1 mesaj olmalı)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1) 
        self.assertEqual(str(messages[0]), 'Geçersiz kupon kodu.')

        # 4. İndirimin uygulanmadığını kontrol et
        cart = response.context['cart']
        self.assertEqual(cart.get_discount(), Decimal('0'))
        self.assertEqual(cart.get_total_price_after_discount(), Decimal('200.00'))
        
        print("PASSED: Geçersiz Kupon Testi")