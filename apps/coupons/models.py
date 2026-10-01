from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Coupon(models.Model):

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
    ]

    code = models.CharField(
        max_length=50,
        unique=True,
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default="percentage",
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
        ],
    )

    minimum_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0),
        ],
    )

    maximum_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
        ],
    )

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    used_count = models.PositiveIntegerField(
        default=0,
    )

    valid_from = models.DateTimeField()

    valid_until = models.DateTimeField()

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        now = timezone.now()

        if not self.is_active:
            return False

        if now < self.valid_from:
            return False

        if now > self.valid_until:
            return False

        if (
            self.usage_limit is not None
            and self.used_count >= self.usage_limit
        ):
            return False

        return True