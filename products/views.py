from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Product, Category
from django.core.paginator import Paginator
from django.db.models import Q, Min, Avg, Sum, Count # Hesaplama fonksiyonları
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .filters import ProductFilter 
from .models import Review
from .forms import ReviewForm
from orders.models import OrderItem 
from .forms import StockNotificationForm
from .models import StockNotification, ProductVariant # ProductVariant eklendi

# ==================================================
# === YARDIMCI FONKSİYON ===
# ==================================================
def get_all_descendant_categories(category):
    descendants = [category]
    for child in category.children.all():
        descendants.extend(get_all_descendant_categories(child))
    return descendants

# ==================================================
# === GÜNCELLENEN product_list FONKSİYONU ===
# ==================================================
def product_list(request, category_slug=None):
    # 1. Tüm Ana Kategorileri Al (Filtre ağacı için)
    # prefetch_related ile alt kategorileri de peşin çekiyoruz ki veritabanını yormasın
    main_categories = Category.objects.filter(parent=None).prefetch_related('children__children')
    
    current_category = None
    
    # 2. Temel Ürün Listesi
    product_list = Product.objects.filter(variants__isnull=False).distinct()
    
    # 3. Eğer URL'den kategori geldiyse (/products/erkek/ gibi)
    # Bunu başlangıç filtresi olarak ayarla ama kullanıcı değiştirebilsin
    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        # URL'den gelen kategori sayfayı daraltır ama filtre nesnesi (checkbox) bunu yönetecek.
        # Ancak "Breadcrumb" veya başlık için current_category'yi tutuyoruz.
        
        # NOT: Eğer kullanıcı URL'den geldiyse, o kategorinin ürünlerini getir.
        # Ancak filtre formunda da o kutucuğun işaretli olmasını şablonda halledeceğiz.
        categories_to_filter = get_all_descendant_categories(current_category)
        
        # Eğer GET parametrelerinde 'category' yoksa, URL'den geleni uygula
        if 'category' not in request.GET:
            product_list = product_list.filter(
                Q(category__in=categories_to_filter) | 
                Q(secondary_categories__in=categories_to_filter)
            ).distinct()

    # 4. Arama Mantığı
    query = request.GET.get('q')
    if query:
        product_list = product_list.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query) | 
            Q(variants__sku__icontains=query) | 
            Q(variants__color__name__icontains=query) 
        ).distinct()

    # 5. Filtreleme (django-filters)
    # Burası checkbox'lardan gelen veriyi işler
    product_filter = ProductFilter(request.GET, queryset=product_list)
    product_list = product_filter.qs

    # 6. Sıralama ve Hesaplama (Annotation)
    product_list = product_list.annotate(
        min_price=Min('variants__price'),
        avg_rating=Avg('reviews__rating'),
        total_sold=Sum('order_items__quantity', filter=Q(order_items__order__paid=True)) 
    )

    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_asc':
        product_list = product_list.order_by('min_price')
    elif sort_by == 'price_desc':
        product_list = product_list.order_by('-min_price')
    elif sort_by == 'rating':
        product_list = product_list.order_by('-avg_rating')
    elif sort_by == 'bestseller':
        product_list = product_list.order_by('-total_sold')
    else:
        product_list = product_list.order_by('-created_at')

    # 7. Sayfalama
    paginator = Paginator(product_list, 12) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'query': query,
        'main_categories': main_categories, # Ağaç yapısı için
        'current_category': current_category,
        'product_filter': product_filter,
        'current_sort': sort_by, 
    }
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
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
    product_images = product.images.all()
    similar_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]

    reviews = product.reviews.all()
    review_form = ReviewForm()
    user_can_review = False 
    user_has_reviewed = False 

    if request.user.is_authenticated:
        if reviews.filter(user=request.user).exists():
            user_has_reviewed = True
        else:
            has_purchased = OrderItem.objects.filter(
                order__user=request.user, 
                product=product, 
                order__paid=True
            ).exists()
            if has_purchased:
                user_can_review = True

    if request.method == 'POST' and user_can_review:
        form = ReviewForm(request.POST)
        if form.is_valid():
            try:
                new_review = form.save(commit=False)
                new_review.product = product
                new_review.user = request.user
                new_review.save()
                messages.success(request, "Değerlendirmeniz için teşekkür ederiz!")
                return redirect(product.get_absolute_url())
            except: 
                messages.error(request, "Bu ürünü zaten değerlendirdiniz.")
        else:
            messages.error(request, "Formda hatalar var.")
            review_form = form 

    context = {
        'product': product,
        'variants': variants_list,
        'product_images': product_images,
        'similar_products': similar_products,
        'reviews': reviews,
        'review_form': review_form,
        'user_can_review': user_can_review,
        'user_has_reviewed': user_has_reviewed,
    }
    return render(request, 'products/product_detail.html', context)

def product_quick_view(request, slug):
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
    favourite_products = request.user.favourite_products.all()
    context = {'favourite_products': favourite_products}
    return render(request, 'products/favourite_list.html', context)

def stock_notification_request(request):
    """
    AJAX ile gelen stok bildirimi talebini kaydeder.
    """
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        variant_id = request.POST.get('variant_id')
        email = request.POST.get('email')
        
        if not variant_id or not email:
            return JsonResponse({'status': 'error', 'message': 'Eksik bilgi.'}, status=400)
            
        variant = get_object_or_404(ProductVariant, id=variant_id)
        
        # Zaten kayıt var mı kontrol et
        if StockNotification.objects.filter(variant=variant, email=email, is_notified=False).exists():
            return JsonResponse({'status': 'warning', 'message': 'Bu ürün için zaten talebiniz var.'})
            
        StockNotification.objects.create(variant=variant, email=email)
        return JsonResponse({'status': 'ok', 'message': 'Talebiniz alındı. Stok gelince haber vereceğiz!'})
        
    return JsonResponse({'status': 'error', 'message': 'Geçersiz istek.'}, status=400)

def live_search(request):
    """
    AJAX ile anlık arama sonuçlarını döndürür.
    """
    query = request.GET.get('q', '')
    results = []
    
    if len(query) > 2: # En az 3 karakter yazılınca ara
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) |
            Q(variants__sku__icontains=query)
        ).distinct()[:5] # En fazla 5 sonuç göster
        
        for product in products:
            # İlk varyantın fiyatını al
            first_variant = product.variants.first()
            price = first_variant.price if first_variant else 0
            
            results.append({
                'name': product.name,
                'url': product.get_absolute_url(),
                'image': product.image.url if product.image else '/static/images/placeholder.png',
                'price': price
            })
            
    return JsonResponse({'results': results})