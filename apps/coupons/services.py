from decimal import Decimal

from django.utils import timezone

from .models import Coupon


class CouponValidationError(Exception):
    pass


def get_valid_coupon(code, subtotal):

    if not code:
        raise CouponValidationError(
            "Please enter a coupon code."
        )

    code = str(code).strip().upper()

    try:
        coupon = Coupon.objects.get(
            code__iexact=code
        )

    except Coupon.DoesNotExist:
        raise CouponValidationError(
            "Invalid coupon code."
        )

    now = timezone.now()

    if not coupon.is_active:
        raise CouponValidationError(
            "This coupon is no longer active."
        )

    if now < coupon.valid_from:
        raise CouponValidationError(
            "This coupon is not active yet."
        )

    if now > coupon.valid_until:
        raise CouponValidationError(
            "This coupon has expired."
        )

    if (
        coupon.usage_limit is not None
        and coupon.used_count >= coupon.usage_limit
    ):
        raise CouponValidationError(
            "This coupon has reached its usage limit."
        )

    subtotal = Decimal(str(subtotal))

    if subtotal < coupon.minimum_order_amount:
        raise CouponValidationError(
            f"Minimum order amount is "
            f"৳{coupon.minimum_order_amount}."
        )

    return coupon


def calculate_discount(coupon, subtotal):

    subtotal = Decimal(str(subtotal))

    if coupon.discount_type == "percentage":

        discount = (
            subtotal
            * coupon.discount_value
            / Decimal("100")
        )

        if coupon.maximum_discount is not None:

            discount = min(
                discount,
                coupon.maximum_discount,
            )

    else:

        discount = coupon.discount_value

    discount = min(
        discount,
        subtotal,
    )

    return discount.quantize(
        Decimal("0.01")
    )


def calculate_final_total(
    subtotal,
    discount,
):

    subtotal = Decimal(str(subtotal))
    discount = Decimal(str(discount))

    total = subtotal - discount

    return max(
        total,
        Decimal("0.00"),
    ).quantize(
        Decimal("0.01")
    )