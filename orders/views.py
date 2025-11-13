from django.shortcuts import render, redirect, get_object_or_404
# login_required'ı hala order_history için kullanıyoruz, o yüzden import kalsın
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem
from .forms import OrderCreateForm, OrderTrackingForm
from cart.cart import Cart
from django.contrib import messages
from django.conf import settings
from django.urls import reverse
import stripe

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from django.db import transaction 
from products.models import ProductVariant 

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION

# ==================================================
# === GÜNCELLENEN CHECKOUT FONKSİYONU ===
# ==================================================

# @login_required DEKORATÖRÜ BURADAN KALDIRILDI
def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Ödeme yapmak için sepetinizde ürün olmalı.")
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            
            # Bu mantık zaten misafirleri destekliyordu:
            if request.user.is_authenticated:
                order.user = request.user
            
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.coupon.discount
                
            order.shipping_cost = cart.get_shipping_fee()
            order.save() 

            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['variant'].product,
                    variant=item['variant'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            
            cart.clear()
            
            if request.session.get('coupon_id'):
                del request.session['coupon_id']
                request.session.modified = True

            request.session['order_id'] = order.id
            
            return redirect('orders:payment_process')

    else:
        # === MİSAFİR KULLANICI İÇİN GET MANTIĞI GÜNCELLENDİ ===
        form = OrderCreateForm() # Önce boş bir form oluştur
        
        # Eğer kullanıcı giriş yapmışsa, formu doldurmayı dene
        if request.user.is_authenticated:
            try:
                profile = request.user.userprofile
                initial_data = {
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    'address': profile.address_detail,
                    'postal_code': profile.postal_code,
                    'city': profile.city,
                }
                form = OrderCreateForm(initial=initial_data) # Formu dolu olanla değiştir
            except:
                 # Profili (henüz) yoksa, boş formu kullanmaya devam et
                 pass
        # === GÜNCELLEME SONU ===

    return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
# ==================================================
# === GÜNCELLEME SONU ===
# ==================================================


def payment_process(request):
    # ... (Bu fonksiyonda değişiklik yok) ...
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('pages:home')
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, "Ödeme yapılacak sipariş bulunamadı.")
        return redirect('cart:cart_detail')
    if request.method == 'GET':
        success_url = request.build_absolute_uri(reverse('orders:payment_done'))
        cancel_url = request.build_absolute_uri(reverse('orders:payment_canceled'))
        line_items = []
        for item in order.items.all():
            line_items.append({
                'price_data': {
                    'currency': 'try', 
                    'product_data': { 'name': f"{item.product.name} ({item.variant.size.name} / {item.variant.color.name})", },
                    'unit_amount': int(item.price * 100), 
                },
                'quantity': item.quantity,
            })
        if order.shipping_cost > 0:
            line_items.append({
                'price_data': {
                    'currency': 'try',
                    'product_data': { 'name': "Kargo Ücreti", },
                    'unit_amount': int(order.shipping_cost * 100),
                },
                'quantity': 1,
            })
        coupon_data = {}
        if order.coupon:
            stripe_coupon = stripe.Coupon.create(
                percent_off=order.discount,
                duration='once', 
                name=order.coupon.code
            )
            coupon_data = {'coupon': stripe_coupon.id}
        try:
            session_params = {
                'payment_method_types': ['card'],
                'mode': 'payment',
                'line_items': line_items,
                'customer_email': order.email, 
                'success_url': success_url,
                'cancel_url': cancel_url,
            }
            if coupon_data:
                session_params['discounts'] = [coupon_data]
            session = stripe.checkout.Session.create(**session_params)
            return redirect(session.url, code=303)
        except stripe.error.StripeError as e:
            messages.error(request, f"Stripe ile bağlantı kurulamadı: {e}")
            return redirect('cart:cart_detail')
        except Exception as e:
            messages.error(request, f"Bir hata oluştu: {e}")
            return redirect('cart:cart_detail')
    else:
        return redirect('pages:home')

@transaction.atomic 
def payment_done(request):
    # ... (Bu fonksiyonda değişiklik yok, stok düşürme dahil) ...
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
            if not order.paid: 
                order.paid = True
                order.status = 'processing' 
                order.save()
                
                for item in order.items.all():
                    try:
                        variant = item.variant
                        if variant.stock >= item.quantity:
                            variant.stock -= item.quantity
                        else:
                            variant.stock = 0
                        variant.save()
                    except ProductVariant.DoesNotExist:
                        print(f"Stok düşürme hatası: Varyant bulunamadı. Sipariş #{order.id}")
                        pass
                
                try:
                    context = {'order': order}
                    subject = render_to_string('orders/email/order_confirmation_subject.txt', context).strip()
                    html_message = render_to_string('orders/email/order_confirmation_body.html', context)
                    plain_message = strip_tags(html_message) 
                    send_mail(
                        subject=subject, message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[order.email], 
                        html_message=html_message,
                        fail_silently=False 
                    )
                except Exception as e:
                    print(f"Hata: Sipariş #{order.id} için e-posta gönderilemedi. Hata: {e}")

            if 'order_id' in request.session:
                del request.session['order_id']
            if 'coupon_id' in request.session:
                del request.session['coupon_id']
            
            return render(request, 'orders/done.html', {'order_id': order.id})
        
        except Order.DoesNotExist:
            pass 
            
    return render(request, 'orders/done.html')


def payment_canceled(request):
    # ... (Bu fonksiyonda değişiklik yok) ...
    order_id = request.session.get('order_id')
    if order_id:
        try:
            order = Order.objects.get(id=order_id, paid=False)
            order.delete() 
            messages.warning(request, "Ödeme iptal edildi. Ödenmemiş siparişiniz silindi.")
        except Order.DoesNotExist:
            pass
        if 'order_id' in request.session:
            del request.session['order_id']
        if 'coupon_id' in request.session:
            del request.session['coupon_id']
        request.session.modified = True
    return render(request, 'orders/canceled.html')

@login_required # Bu @login_required kalmalı (Sadece giriş yapanlar geçmişini görür)
def order_history(request):
    orders = Order.objects.filter(user=request.user, paid=True)
    return render(request, 'orders/history.html', {'orders': orders})

def order_tracking_view(request):
    # ... (Bu fonksiyonda değişiklik yok) ...
    order = None
    if request.method == 'POST':
        form = OrderTrackingForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data['order_id']
            email = form.cleaned_data['email']
            if order_id.startswith('#'):
                order_id = order_id[1:]
            try:
                order = Order.objects.get(id=order_id, email=email)
            except Order.DoesNotExist:
                messages.error(request, "Bu bilgilere sahip bir sipariş bulunamadı.")
    else:
        form = OrderTrackingForm()
    return render(request, 'orders/order_tracking.html', {'form': form, 'order': order})