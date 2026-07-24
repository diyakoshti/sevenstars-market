from decimal import Decimal
import hashlib
import uuid
import razorpay
from django.conf import settings
from django.core import signing
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from cart.models import CartItem
from products.models import Product
from .forms import CheckoutForm
from .models import Order, OrderItem


def _client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def checkout(request):
    items = list(CartItem.objects.filter(user=request.user).select_related("product"))
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("cart:detail")
    total = sum(item.subtotal for item in items)
    form = CheckoutForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if settings.DEMO_PAYMENT_MODE:
            demo_order_id = f"demo_order_{uuid.uuid4().hex[:16]}"
            token = signing.dumps({
                "order_id": demo_order_id,
                "user_id": request.user.pk,
                "total": str(total),
            })
            request.session["checkout_address"] = form.cleaned_data["shipping_address"]
            return render(request, "orders/demo_payment.html", {
                "items": items,
                "total": total,
                "demo_order_id": demo_order_id,
                "demo_token": token,
            })
        if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
            messages.error(request, "Razorpay test keys are not configured in .env.")
        elif any(item.quantity > item.product.stock for item in items):
            messages.error(request, "One or more products no longer have enough stock.")
        else:
            gateway_order = _client().order.create({
                "amount": int(total * Decimal("100")),
                "currency": "INR",
                "receipt": f"user-{request.user.pk}",
            })
            request.session["checkout_address"] = form.cleaned_data["shipping_address"]
            return render(request, "orders/payment.html", {
                "items": items,
                "total": total,
                "razorpay_order_id": gateway_order["id"],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount_paise": gateway_order["amount"],
            })
    return render(request, "orders/checkout.html", {"items": items, "total": total, "form": form})


@login_required
@transaction.atomic
def demo_payment(request):
    if request.method != "POST" or not settings.DEMO_PAYMENT_MODE:
        return redirect("cart:detail")
    if request.POST.get("result") == "failure":
        messages.error(request, "Demo payment failed. No order was created and your cart is unchanged.")
        return redirect("cart:detail")
    token = request.POST.get("demo_token", "")
    try:
        payload = signing.loads(token, max_age=600)
    except signing.BadSignature:
        messages.error(request, "Demo payment verification failed.")
        return redirect("cart:detail")
    if payload.get("user_id") != request.user.pk:
        messages.error(request, "This demo payment does not belong to your account.")
        return redirect("cart:detail")

    payment_data = {
        "razorpay_order_id": payload["order_id"],
        "razorpay_payment_id": f"demo_pay_{uuid.uuid4().hex[:16]}",
        "razorpay_signature": hashlib.sha256(token.encode()).hexdigest(),
    }
    return _complete_verified_order(request, payment_data)


def _complete_verified_order(request, payment_data):
    if Order.objects.filter(razorpay_payment_id=payment_data["razorpay_payment_id"]).exists():
        messages.info(request, "This payment has already been processed.")
        return redirect("orders:history")
    cart_items = list(CartItem.objects.filter(user=request.user).select_related("product"))
    if not cart_items:
        messages.error(request, "Your cart is empty.")
        return redirect("cart:detail")
    locked_products = {
        product.pk: product
        for product in Product.objects.select_for_update().filter(pk__in=[i.product_id for i in cart_items])
    }
    for item in cart_items:
        if locked_products[item.product_id].stock < item.quantity:
            messages.error(request, f"Not enough stock for {item.product.name}.")
            transaction.set_rollback(True)
            return redirect("cart:detail")
    total = sum(item.product.price * item.quantity for item in cart_items)
    order = Order.objects.create(
        user=request.user,
        total_amount=total,
        shipping_address=request.session.pop("checkout_address", "Address not provided"),
        **payment_data,
    )
    for item in cart_items:
        product = locked_products[item.product_id]
        OrderItem.objects.create(
            order=order,
            product=product,
            seller=product.owner,
            product_name=product.name,
            price=product.price,
            quantity=item.quantity,
        )
        product.stock -= item.quantity
        product.save(update_fields=["stock"])
    CartItem.objects.filter(user=request.user).delete()
    messages.success(request, f"Demo payment verified! Order #{order.pk} was created.")
    return redirect("orders:history")


@login_required
@transaction.atomic
def verify_payment(request):
    if request.method != "POST":
        return redirect("cart:detail")
    data = {
        "razorpay_order_id": request.POST.get("razorpay_order_id", ""),
        "razorpay_payment_id": request.POST.get("razorpay_payment_id", ""),
        "razorpay_signature": request.POST.get("razorpay_signature", ""),
    }
    try:
        _client().utility.verify_payment_signature(data)
    except razorpay.errors.SignatureVerificationError:
        messages.error(request, "Payment verification failed. Order was not created.")
        return redirect("cart:detail")

    return _complete_verified_order(request, data)


@login_required
def history(request):
    return render(request, "orders/history.html", {
        "orders": Order.objects.filter(user=request.user).prefetch_related("items")
    })
