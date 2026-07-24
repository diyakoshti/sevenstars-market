from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ProductForm
from .models import Category, Product
from .permissions import seller_or_admin_required


def product_list(request):
    products = Product.objects.filter(is_active=True).select_related("category", "owner")
    keyword = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()
    if keyword:
        products = products.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
    if category:
        products = products.filter(category__slug=category)
    try:
        if min_price:
            products = products.filter(price__gte=Decimal(min_price))
        if max_price:
            products = products.filter(price__lte=Decimal(max_price))
    except InvalidOperation:
        messages.error(request, "Please enter a valid price.")
    return render(request, "products/list.html", {
        "products": products,
        "categories": Category.objects.all(),
    })


def product_detail(request, slug):
    product = get_object_or_404(Product.objects.select_related("category", "owner"), slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "products/detail.html", {"product": product, "related_products": related})


@login_required
@seller_or_admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        product.owner = request.user
        product.save()
        messages.success(request, "Product added successfully.")
        return redirect(product)
    return render(request, "products/form.html", {"form": form, "title": "Add Product"})


def _can_manage(user, product):
    return user.role == "admin" or (user.role == "sales" and product.owner_id == user.id)


@login_required
@seller_or_admin_required
def product_update(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not _can_manage(request.user, product):
        return HttpResponseForbidden("You can edit only your own products.")
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Product updated successfully.")
        return redirect(product)
    return render(request, "products/form.html", {"form": form, "title": "Edit Product"})


@login_required
@seller_or_admin_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    if not _can_manage(request.user, product):
        return HttpResponseForbidden("You can delete only your own products.")
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully.")
        return redirect("products:list")
    return render(request, "products/delete.html", {"product": product})
