from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from products.models import Product, ProductVariant
from .cart import Cart
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone # YENİ: Zaman kontrolü için
from django.template.loader import render_to_string
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
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    # Stok Kontrolü
    current_qty_in_cart = cart.cart.get(str(variant_id), {}).get('quantity', 0)
    if current_qty_in_cart + quantity > variant.stock:
        return JsonResponse({
            'status': 'error',
            'message': f'Stok yetersiz! En fazla {variant.stock} adet alabilirsiniz.'
        }, status=400)

    cart.add(variant=variant, quantity=quantity)

    # --- GÜNCELLEME: Yeni HTML'i Hazırla ---
    # Sepetin güncel halini HTML olarak render et
    cart_html = render_to_string('cart/partials/offcanvas_body.html', {'cart': cart}, request=request)
    
    return JsonResponse({
        'status': 'ok',
        'message': 'Ürün sepete eklendi.',
        'cart_total_items': len(cart),
        'cart_html': cart_html  # HTML'i frontend'e gönder
    })

@require_POST
def cart_remove(request, variant_id):
    cart = Cart(request)
    variant = get_object_or_404(ProductVariant, id=variant_id)
    cart.remove(variant)
    
    # --- GÜNCELLEME: Yeni HTML'i Hazırla ---
    cart_html = render_to_string('cart/partials/offcanvas_body.html', {'cart': cart}, request=request)

    return JsonResponse({
        'status': 'ok',
        'message': 'Ürün sepetten çıkarıldı.',
        'cart_total_items': len(cart),
        'cart_html': cart_html # HTML'i frontend'e gönder
    })


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