from decimal import Decimal
from django.contrib import messages
from django.shortcuts import redirect

from apps.cart.services import get_or_create_cart

from apps.cart.models import CartItem
from .cart import apply_coupon as apply_coupon_to_cart
from .cart import remove_coupon as remove_coupon_from_cart
from .forms import CouponApplyForm
from .services import CouponValidationError
from apps.coupons.services import CouponValidationError


def apply_coupon(request):

    if request.method != "POST":
        return redirect("cart_detail")

    form = CouponApplyForm(request.POST)

    if not form.is_valid():
        messages.error(
            request,
            "Please enter a valid coupon code.",
        )
        return redirect("cart_detail")

    code = form.cleaned_data["code"].strip().upper()

    cart = get_or_create_cart(request)

    items = cart.items.select_related(
        "variant",
        "variant__product",
    )

    subtotal = Decimal("0.00")

    for item in items:
        subtotal += (
            item.variant.price * item.quantity
        )

    try:

        coupon, discount = apply_coupon_to_cart(
            request,
            code,
            subtotal,
        )

        messages.success(
            request,
            f"Coupon {coupon.code} applied successfully. "
            f"You saved ৳{discount}.",
        )

    except CouponValidationError as e:

        messages.error(
            request,
            str(e),
        )

    return redirect("cart_detail")


def remove_coupon(request):

    if request.method == "POST":

        remove_coupon_from_cart(request)

        messages.success(
            request,
            "Coupon removed successfully.",
        )

    return redirect("cart_detail")

def remove_coupon(request):

    if request.method == "POST":

        remove_coupon_from_cart(
            request
        )

        messages.success(
            request,
            "Coupon removed.",
        )

    return redirect("cart_detail")