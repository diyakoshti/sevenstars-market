from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("products/", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("orders/", include("orders.urls")),
    path("dashboard/", include("dashboard.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "SevenStars Market Administration"
admin.site.site_title = "SevenStars Admin"
admin.site.index_title = "Store Management"
