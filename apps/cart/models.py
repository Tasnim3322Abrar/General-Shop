from django.conf import settings
from django.db import models

from apps.store.models import ProductVariant


class Cart(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cart",
    )

    session_key = models.CharField(
        max_length=40,
        unique=True,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        if self.user:
            return f"Cart - {self.user.username}"

        return f"Guest Cart - {self.session_key}"

    @property
    def total_quantity(self):
        return sum(
            item.quantity
            for item in self.items.all()
        )

    @property
    def subtotal(self):
        return sum(
            item.subtotal
            for item in self.items.all()
        )


class CartItem(models.Model):

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="cart_items",
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-added_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["cart", "variant"],
                name="unique_cart_variant",
            )
        ]

    @property
    def unit_price(self):
        return self.variant.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return (
            f"{self.variant.product.name} "
            f"- {self.variant.name}"
        )