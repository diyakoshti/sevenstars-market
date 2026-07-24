from django.urls import path
from . import views

app_name = "orders"
urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("demo-payment/", views.demo_payment, name="demo_payment"),
    path("verify-payment/", views.verify_payment, name="verify_payment"),
    path("history/", views.history, name="history"),
]
