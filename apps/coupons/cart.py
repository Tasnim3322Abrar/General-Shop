from decimal import Decimal

from .services import (
    CouponValidationError,
    calculate_discount,
    get_valid_coupon,
)


COUPON_SESSION_KEY = "coupon_code"


def apply_coupon(request, code, subtotal):

    coupon = get_valid_coupon(
        code,
        subtotal,
    )

    discount = calculate_discount(
        coupon,
        subtotal,
    )

    request.session[COUPON_SESSION_KEY] = coupon.code
    request.session.modified = True

    return coupon, discount


def remove_coupon(request):

    request.session.pop(
        COUPON_SESSION_KEY,
        None,
    )

    request.session.modified = True


def get_applied_coupon(request, subtotal):

    code = request.session.get(
        COUPON_SESSION_KEY
    )

    if not code:
        return None, Decimal("0.00")

    try:

        coupon = get_valid_coupon(
            code,
            subtotal,
        )

        discount = calculate_discount(
            coupon,
            subtotal,
        )

        return coupon, discount

    except CouponValidationError:

        remove_coupon(request)

        return None, Decimal("0.00")