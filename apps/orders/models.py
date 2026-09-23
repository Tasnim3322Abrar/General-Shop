from django.conf import settings
from django.db import models

from apps.store.models import ProductVariant


class Address(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses",
    )

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=30
    )

    address_line = models.TextField()

    city = models.CharField(
        max_length=100
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True,
    )

    is_default = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    DELIVERY_CHOICES = [
        ("delivery", "Delivery"),
        ("pickup", "Store Pickup"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.PROTECT,
        related_name="orders",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    delivery_method = models.CharField(
        max_length=20,
        choices=DELIVERY_CHOICES,
        default="delivery",
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    delivery_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    notes = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.PROTECT,
        related_name="order_items",
    )

    product_name = models.CharField(
        max_length=250
    )

    variant_name = models.CharField(
        max_length=150,
        blank=True,
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"