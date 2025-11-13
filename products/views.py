from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .filters import ProductFilter 
from .models import Review
from .forms import ReviewForm
from orders.models import OrderItem # Satın alma kontrolü için

# ==================================================
# === YENİ YARDIMCI FONKSİYON ===
# ==================================================
def get_all_descendant_categories(category):
    """
    Verilen bir kategorinin kendisi de dahil olmak üzere
    tüm alt kategorilerini (torunlar vb.) özyinelemeli (recursive)
    olarak bulan bir fonksiyon.
    """
    descendants = [category] # Kategoriye doğrudan atanan ürünleri de dahil et
    
    # Modelinizde 'children' olarak related_name tanımlamıştık
    for child in category.children.all():
        descendants.extend(get_all_descendant_categories(child))
        
    return descendants
# ==================================================


# ==================================================
# === GÜNCELLENEN product_list FONKSİYONU ===
# ==================================================
def product_list(request, category_slug=None):
    current_category = None
    categories = Category.objects.all()
    product_list = Product.objects.filter(variants__isnull=False).distinct().order_by('-created_at')
    product_list = product_list.prefetch_related('images', 'variants')
    
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        
        # 1. Tıklanan kategori ve TÜM alt kategorilerini (torunlar dahil) al.
        categories_to_filter = get_all_descendant_categories(current_category)
        
        # ============================================
        # === YENİ FİLTRELEME MANTIĞI ===
        # ============================================
        # Ürünleri, Ana Kategorisi VEYA İkincil Kategorisi
        # bu listede olanlara göre filtrele.
        product_list = product_list.filter(
            Q(category__in=categories_to_filter) | 
            Q(secondary_categories__in=categories_to_filter)
        ).distinct() # Tekrar distinct() kullanmak önemlidir
        # ============================================

    # --- Arama Mantığı (Değişiklik Yok) ---
    query = request.GET.get('q')
    if query:
        product_list = product_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query) | 
            Q(variants__sku__icontains=query) | 
            Q(variants__color__name__icontains=query) | 
            Q(variants__size__name__icontains=query) 
        ).distinct()
    # --- Arama Mantığı Sonu ---

    # --- Filtreleme Adımı (Değişiklik Yok) ---
    product_filter = ProductFilter(request.GET, queryset=product_list)
    
    paginator = Paginator(product_filter.qs, 6) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'current_category': current_category,
        'product_filter': product_filter, 
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    # Mevcut varyant ve resim kodları (Değişiklik yok)
    variants_queryset = product.variants.select_related('color', 'size').all()
    variants_list = []
    for v in variants_queryset:
        variants_list.append({
            'id': v.id, 'size': v.size.name if v.size else None,
            'color': v.color.name if v.color else None,
            'hex_code': v.color.hex_code if v.color else '#CCCCCC',
            'stock': v.stock, 'price': v.price
        })
    product_images = product.images.all()
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    # --- YENİ DEĞERLENDİRME MANTIĞI ---
    reviews = product.reviews.all()
    review_form = ReviewForm()
    user_can_review = False # Varsayılan
    user_has_reviewed = False # Varsayılan

    if request.user.is_authenticated:
        # 1. Kullanıcı bu ürünü daha önce değerlendirmiş mi?
        if reviews.filter(user=request.user).exists():
            user_has_reviewed = True
        
        # 2. Değerlendirmemişse, satın almış mı diye kontrol et
        else:
            has_purchased = OrderItem.objects.filter(
                order__user=request.user, 
                product=product, 
                order__paid=True
            ).exists()
            
            if has_purchased:
                user_can_review = True

    # --- YENİ POST İŞLEMCİSİ ---
    if request.method == 'POST' and user_can_review:
        # Formu sadece yorum yapabilenler (satın alanlar) gönderebilir
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                new_review = form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                messages.success(request, "Değerlendirmeniz için teşekkür ederiz!")
                return redirect(product.get_absolute_url())
            except: # unique_together hatasını yakala (örn: çift tıklama)
                messages.error(request, "Bu ürünü zaten değerlendirdiniz.")
        else:
            messages.error(request, "Formda hatalar var. Lütfen puan seçtiğinizden emin olun.")
            review_form = form # Hatalı formu tekrar göster
    # --- DEĞERLENDİRME MANTIĞI SONU ---

    context = {
        'product': product,
        'variants': variants_list,
        'product_images': product_images,
        'similar_products': similar_products,
        
        # YENİ CONTEXT DEĞİŞKENLERİ
        'reviews': reviews,
        'review_form': review_form,
        'user_can_review': user_can_review,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'products/product_detail.html', context)

def product_quick_view(request, slug):
    # ... (Bu fonksiyonda değişiklik yok) ...
    product = get_object_or_404(Product, slug=slug)
    variants_queryset = product.variants.select_related('color', 'size').all()
    variants_list = []
    for v in variants_queryset:
        variants_list.append({
            'id': v.id, 'size': v.size.name if v.size else None,
            'color': v.color.name if v.color else None,
            'hex_code': v.color.hex_code if v.color else '#CCCCCC',
            'stock': v.stock, 'price': v.price
        })
    images_list = [img.image.url for img in product.images.all()]
    main_image_url = product.image.url if product.image else None
    data = {
        'name': product.name, 'description': product.description,
        'category': str(product.category), 'main_image': main_image_url,
        'gallery_images': images_list, 'variants': variants_list,
        'add_to_cart_url_base': reverse('cart:cart_add', args=[0]),
    }
    return JsonResponse(data)


@login_required
def toggle_favourite(request, product_slug):
    # ... (Bu fonksiyonda değişiklik yok) ...
    product = get_object_or_404(Product, slug=product_slug)
    is_favourited = False
    message = ""
    if product.favourited_by.filter(id=request.user.id).exists():
        product.favourited_by.remove(request.user)
        message = f"'{product.name}' favorilerinizden kaldırıldı."
    else:
        product.favourited_by.add(request.user)
        message = f"'{product.name}' favorilerinize eklendi."
        is_favourited = True
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok', 'message': message,
            'is_favourited': is_favourited
        })
    messages.success(request, message)
    return redirect(request.META.get('HTTP_REFERER', 'products:product_list'))


@login_required
def favourite_list(request):
    # ... (Bu fonksiyonda değişiklik yok) ...
    favourite_products = request.user.favourite_products.all()
    context = {'favourite_products': favourite_products}
    return render(request, 'products/favourite_list.html', context)