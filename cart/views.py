from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .models import CartItem


@login_required
def detail(request):
    items = CartItem.objects.filter(user=request.user).select_related("product")
    total = sum(item.subtotal for item in items)
    return render(request, "cart/detail.html", {"items": items, "total": total})


@login_required
def add(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if product.stock < 1:
        messages.error(request, "This product is out of stock.")
        return redirect(product)
    item, created = CartItem.objects.get_or_create(user=request.user, product=product)
    if not created:
        if item.quantity >= product.stock:
            messages.error(request, "Maximum available stock is already in your cart.")
            return redirect("cart:detail")
        item.quantity = F("quantity") + 1
        item.save(update_fields=["quantity"])
    messages.success(request, "Product added to cart.")
    return redirect("cart:detail")


@login_required
def update(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    try:
        quantity = int(request.POST.get("quantity", 1))
    except ValueError:
        quantity = 1
    if quantity < 1:
        item.delete()
    elif quantity <= item.product.stock:
        item.quantity = quantity
        item.save(update_fields=["quantity"])
    else:
        messages.error(request, "Requested quantity exceeds available stock.")
    return redirect("cart:detail")


@login_required
def remove(request, item_id):
    item = get_object_or_404(CartItem, pk=item_id, user=request.user)
    if request.method == "POST":
        item.delete()
    return redirect("cart:detail")
