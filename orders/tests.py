from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

# Test verisi oluşturmak için modellerimizi import ediyoruz
from products.models import Product, Category, Color, Size, ProductVariant
from orders.models import Order, OrderItem, Coupon

User = get_user_model()

class OrderLogicTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        """
        Tüm testlerin kullanacağı verileri bir kez oluşturur.
        """
        cls.user = User.objects.create_user(username='testuser', password='password123')
        
        cls.category = Category.objects.create(name="Test Kategori", slug="test-kategori")
        cls.color = Color.objects.create(name="Test Renk", hex_code="#FFF")
        cls.size = Size.objects.create(name="Test Beden", slug="test-beden", order=1)
        cls.product = Product.objects.create(category=cls.category, name="Test Gömlek", slug="test-gomlek")
        cls.variant = ProductVariant.objects.create(
            product=cls.product,
            color=cls.color,
            size=cls.size,
            sku="TEST-ORDER",
            price=Decimal('100.00'),
            stock=10
        )
        
        cls.coupon = Coupon.objects.create(
            code="ORDERTEST",
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
            discount=10, # %10 indirim
            active=True
        )
        
        cls.valid_checkout_data = {
            'first_name': 'Test',
            'last_name': 'Kullanıcı',
            'email': 'test@kullanici.com',
            'address': 'Test mahallesi, 123. sokak',
            'postal_code': '34000',
            'city': 'Istanbul',
        }

    def setUp(self):
        """Her testten önce temiz bir client oluştur."""
        self.client = Client()

    def test_checkout_requires_login(self):
        """Test 1: Giriş yapmayan kullanıcı checkout'a gidememeli."""
        
        response = self.client.get(reverse('orders:checkout'))
        
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('orders:checkout')}")
        
        print("\nPASSED: Checkout Giriş Kontrolü Testi")

    def test_checkout_empty_cart(self):
        """Test 2: Giriş yapmış ama sepeti boş olan kullanıcı checkout'a gidememeli."""
        
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('orders:checkout'), follow=True)
        
        self.assertRedirects(response, reverse('cart:cart_detail'))
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Ödeme yapmak için sepetinizde ürün olmalı.")
        
        print("PASSED: Checkout Boş Sepet Testi")

    def test_order_creation_with_coupon(self):
        """Test 3: Sepeti dolu ve kuponlu kullanıcının sipariş oluşturmasını test et."""
        
        self.client.login(username='testuser', password='password123')
        
        session = self.client.session
        session[settings.CART_SESSION_ID] = {
            str(self.variant.id): {'quantity': 2, 'price': str(self.variant.price)}
        }
        session['coupon_id'] = self.coupon.id 
        session.save()

        # Checkout sayfasına POST isteği gönder (Siparişi oluştur)
        response = self.client.post(reverse('orders:checkout'), self.valid_checkout_data)
        
        # ============================================
        # === GÜNCELLEME BURADA: (302 != 200 Hatası için) ===
        # ============================================
        
        # HATA DÜZELTMESİ: Yönlendirmeyi takip etme.
        # Sadece status code'un 302 (Redirect) olduğunu kontrol et.
        self.assertEqual(response.status_code, 302)
        
        # Yönlendirildiği yerin 'payment_process' olduğunu kontrol et.
        self.assertEqual(response.url, reverse('orders:payment_process'))
        
        # ============================================
        # === GÜNCELLEME SONU ===
        # ============================================

        # Siparişin veritabanında oluştuğunu doğrula
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        
        # Siparişin doğru kaydedildiğini doğrula
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.email, 'test@kullanici.com')
        self.assertEqual(order.coupon, self.coupon) 
        self.assertEqual(order.discount, 10) 
        
        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.product)
        self.assertEqual(order_item.quantity, 2)
        
        self.assertNotIn(settings.CART_SESSION_ID, self.client.session)
        self.assertNotIn('coupon_id', self.client.session)
        
        print("PASSED: Kuponlu Sipariş Oluşturma Testi")

    def test_payment_done_logic(self):
        """Test 4: payment_done fonksiyonunun siparişi 'paid' olarak işaretlemesi."""
        
        order = Order.objects.create(
            user=self.user,
            **self.valid_checkout_data 
        )
        self.assertFalse(order.paid) 
        
        session = self.client.session
        session['order_id'] = order.id
        session.save()
        
        response = self.client.get(reverse('orders:payment_done'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'orders/done.html')
        
        order.refresh_from_db() 
        self.assertTrue(order.paid) 
        
        self.assertNotIn('order_id', self.client.session)
        
        print("PASSED: Ödeme Tamamlama (Payment Done) Testi")