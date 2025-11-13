from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from decimal import Decimal

from .models import Product, Category, Color, Size, ProductVariant, Review
from orders.models import Order, OrderItem 

User = get_user_model()

class ProductLogicTests(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password123')
        
        cls.cat_erkek = Category.objects.create(name="Erkek", slug="erkek")
        cls.cat_giysi = Category.objects.create(name="Giysi (Erkek)", slug="erkek-giysi", parent=cls.cat_erkek)
        cls.cat_gomlek = Category.objects.create(name="Gömlek (Erkek)", slug="erkek-gomlek", parent=cls.cat_giysi)
        
        cls.color_beyaz = Color.objects.create(name="Beyaz", hex_code="#FFF")
        cls.color_mavi = Color.objects.create(name="Mavi", hex_code="#00F")
        cls.size_m = Size.objects.create(name="M", slug="m", order=2)

        cls.product_gomlek = Product.objects.create(
            category=cls.cat_gomlek, 
            name="Keten Gömlek",
            slug="keten-gomlek"
        )
        cls.variant_gomlek = ProductVariant.objects.create(
            product=cls.product_gomlek,
            color=cls.color_beyaz,
            size=cls.size_m,
            sku="K-GMK-BYZ",
            price=Decimal('150.00'),
            stock=10
        )
        
        cls.product_pantolon = Product.objects.create(
            category=cls.cat_giysi, 
            name="Keten Pantolon",
            slug="keten-pantolon"
        )
        cls.variant_pantolon = ProductVariant.objects.create(
            product=cls.product_pantolon,
            color=cls.color_mavi,
            size=cls.size_m,
            sku="K-PNT-MVI",
            price=Decimal('200.00'),
            stock=10
        )
        
        cls.order = Order.objects.create(
            user=cls.user,
            first_name="Test", last_name="User", email="test@user.com",
            paid=True 
        )
        OrderItem.objects.create(
            order=cls.order,
            product=cls.product_gomlek, 
            variant=cls.variant_gomlek,
            price=cls.variant_gomlek.price,
            quantity=1
        )

    def setUp(self):
        self.client = Client()

    def test_category_hierarchy_view(self):
        response = self.client.get(reverse('products:product_list_by_category', args=[self.cat_erkek.slug]))
        self.assertContains(response, "Keten Gömlek")
        self.assertContains(response, "Keten Pantolon")
        
        response = self.client.get(reverse('products:product_list_by_category', args=[self.cat_giysi.slug]))
        self.assertContains(response, "Keten Gömlek")
        self.assertContains(response, "Keten Pantolon")
        
        response = self.client.get(reverse('products:product_list_by_category', args=[self.cat_gomlek.slug]))
        self.assertContains(response, "Keten Gömlek")
        self.assertNotContains(response, "Keten Pantolon")
        
        print("\nPASSED: Kategori Hiyerarşisi (Sidebar) Testi")

    def test_smart_search(self):
        response = self.client.get(reverse('products:product_list'), {'q': 'Beyaz'})
        self.assertContains(response, "Keten Gömlek")
        self.assertNotContains(response, "Keten Pantolon")
        
        response = self.client.get(reverse('products:product_list'), {'q': 'K-PNT-MVI'})
        self.assertNotContains(response, "Keten Gömlek")
        self.assertContains(response, "Keten Pantolon")
        
        response = self.client.get(reverse('products:product_list'), {'q': 'Gömlek'})
        self.assertContains(response, "Keten Gömlek")
        self.assertNotContains(response, "Keten Pantolon")
        
        print("PASSED: Akıllı Arama Testi")

    def test_filter(self):
        response = self.client.get(reverse('products:product_list'), {'color': self.color_mavi.id})
        
        self.assertNotContains(response, "Keten Gömlek")
        self.assertContains(response, "Keten Pantolon")
        
        print("PASSED: Filtreleme Testi")

    def test_review_logic_purchased_user(self):
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('products:product_detail', args=[self.product_gomlek.slug]))
        
        self.assertContains(response, "Yorumunuzu buraya yazın...")
        self.assertEqual(response.context['user_can_review'], True)
        
        self.client.post(reverse('products:product_detail', args=[self.product_gomlek.slug]), {
            'rating': 5,
            'comment': 'Harika ürün!'
        })
        
        self.assertTrue(Review.objects.filter(user=self.user, product=self.product_gomlek).exists())
        
        print("PASSED: Yorum Yapma (Satın Alan) Testi")

    # ============================================
    # === GÜNCELLEME BURADA ===
    # ============================================
    def test_review_logic_non_purchased_user(self):
        """Test 5: Satın almayan kullanıcı yorum yapamaz."""
        
        self.client.login(username='testuser', password='password123')
        
        response = self.client.get(reverse('products:product_detail', args=[self.product_pantolon.slug]))
        
        self.assertNotContains(response, "Yorumunuzu buraya yazın...")
        
        # HATA DÜZELTMESİ: HTML etiketleri tarafından bölünmeyecek bir metin arıyoruz.
        self.assertContains(response, "olmanız gerekmektedir")
        
        self.assertEqual(response.context['user_can_review'], False)
        
        self.client.post(reverse('products:product_detail', args=[self.product_pantolon.slug]), {
            'rating': 5,
            'comment': 'Yorum yapmayı deniyorum'
        })
        
        self.assertFalse(Review.objects.filter(user=self.user, product=self.product_pantolon).exists())
        
        print("PASSED: Yorum Engelleme (Satın Almayan) Testi")
    # ============================================