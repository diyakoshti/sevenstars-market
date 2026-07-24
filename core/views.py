from django.shortcuts import render
from products.models import Category, Product


def home(request):
    return render(request, "core/home.html", {
        "featured_products": Product.objects.filter(is_active=True).order_by("-created_at")[:8],
        "categories": Category.objects.all()[:6],
    })
