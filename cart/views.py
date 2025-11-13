from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product, ProductVariant
from .cart import Cart
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone # YENİ: Zaman kontrolü için

# YENİ: Kupon formu ve modelini import et
from orders.forms import CouponApplyForm
from orders.models import Coupon

# ==================================================
# === YENİ KUPON UYGULAMA GÖRÜNÜMÜ ===
# ==================================================
@require_POST
def cart_apply_coupon(request):
    cart = Cart(request)
    form = CouponApplyForm(request.POST)
    
    if form.is_valid():
        code = form.cleaned_data['code']
        
        try:
            # Kuponu koduna göre bul
            # is_valid() metodu ile geçerliliğini kontrol et
            coupon = Coupon.objects.get(code__iexact=code) # Büyük/küçük harf duyarsız
            
            if coupon.is_valid():
                # Kupon geçerliyse, ID'sini session'a kaydet
                request.session['coupon_id'] = coupon.id
                messages.success(request, f"'{coupon.code}' kuponu başarıyla uygulandı.")
            else:
                request.session['coupon_id'] = None
                messages.warning(request, "Bu kuponun süresi dolmuş.")
                
        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None
            messages.error(request, "Geçersiz kupon kodu.")
            
    return redirect('cart:cart_detail')


# ... (Mevcut cart_add, cart_remove, cart_update, cart_detail fonksiyonları) ...

@require_POST
def cart_add(request, variant_id):
    # ... (Mevcut kodunuz) ...
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    if variant.stock < quantity:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Stok yetersiz.'}, status=400)
        messages.error(request, 'Stok yetersiz.')
        return redirect('products:product_detail', slug=variant.product.slug)

    cart.add(variant=variant, quantity=quantity)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'ok',
            'message': 'Ürün sepete eklendi.',
            'cart_total_items': len(cart)
        })
    messages.success(request, 'Ürün sepete eklendi.')
    return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))


@require_POST
def cart_remove(request, variant_id):
    # ... (Mevcut kodunuz) ...
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart.remove(variant)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'reload',
            'message': 'Ürün sepetten kaldırıldı.',
            'cart_total_items': len(cart)
        })
    messages.success(request, 'Ürün sepetten kaldırıldı.')
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, variant_id):
    # ... (Mevcut kodunuz) ...
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart.remove(variant)
        messages.success(request, 'Ürün sepetten kaldırıldı.')
    elif variant.stock < quantity:
        messages.error(request, f"Stokta sadece {variant.stock} adet mevcut.")
    else:
        cart.add(variant=variant, quantity=quantity, override_quantity=True)
        messages.success(request, 'Sepet güncellendi.')
        
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    # YENİ: Kupon formunu bu sayfada da göster
    coupon_apply_form = CouponApplyForm()
    
    return render(request, 'cart/detail.html', {
        'cart': cart,
        'coupon_apply_form': coupon_apply_form # Formu contexte ekle
    })