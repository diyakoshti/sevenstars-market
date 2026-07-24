from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, ExpressionWrapper, F, Sum
from django.http import HttpResponseForbidden
from django.shortcuts import render
from accounts.models import User
from orders.models import Order, OrderItem
from products.models import Product


@login_required
def index(request):
    if request.user.role == User.Role.ADMIN:
        paid_orders = Order.objects.exclude(status=Order.Status.CANCELLED)
        return render(request, "dashboard/admin.html", {
            "total_sales": paid_orders.aggregate(total=Sum("total_amount"))["total"] or 0,
            "total_orders": paid_orders.count(),
            "total_products": Product.objects.count(),
            "total_users": User.objects.filter(role=User.Role.USER).count(),
            "recent_orders": Order.objects.select_related("user")[:8],
        })
    if request.user.role == User.Role.SALES:
        items = OrderItem.objects.filter(seller=request.user).select_related("order", "product", "order__user")
        line_total = ExpressionWrapper(F("price") * F("quantity"), output_field=DecimalField())
        return render(request, "dashboard/sales.html", {
            "items": items,
            "sales_total": items.aggregate(total=Sum(line_total))["total"] or 0,
            "my_products": Product.objects.filter(owner=request.user).count(),
        })
    return HttpResponseForbidden("Dashboard access is restricted to Admin and Sales Person roles.")
