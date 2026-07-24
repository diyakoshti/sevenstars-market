from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product


class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])

    class Meta:
        constraints = [models.UniqueConstraint(fields=["user", "product"], name="unique_cart_product")]

    @property
    def subtotal(self):
        return self.product.price * self.quantity
