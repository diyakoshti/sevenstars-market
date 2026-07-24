from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from products.models import Product
from .models import WishlistItem


@login_required
def detail(request):
    return render(request, "wishlist/detail.html", {
        "items": WishlistItem.objects.filter(user=request.user).select_related("product")
    })


@login_required
def toggle(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    item = WishlistItem.objects.filter(user=request.user, product=product).first()
    if item:
        item.delete()
        messages.info(request, "Removed from wishlist.")
    else:
        WishlistItem.objects.create(user=request.user, product=product)
        messages.success(request, "Added to wishlist.")
    return redirect(request.META.get("HTTP_REFERER", product.get_absolute_url()))
