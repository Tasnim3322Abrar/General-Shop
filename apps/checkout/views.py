from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.services import get_or_create_cart
from apps.coupons.cart import get_applied_coupon
from apps.coupons.services import calculate_final_total
from apps.orders.models import Address, Order, OrderItem


@login_required
def checkout(request):

    cart = get_or_create_cart(request)

    items = (
        cart.items
        .select_related(
            "variant",
            "variant__product",
            "variant__inventory",
        )
        .prefetch_related(
            "variant__product__images",
        )
    )

    if not items.exists():

        messages.warning(
            request,
            "Your cart is empty.",
        )

        return redirect("cart_detail")

    addresses = Address.objects.filter(
        user=request.user,
    ).order_by(
        "-is_default",
        "-created_at",
    )

    selected_address = None

    selected_address_id = request.POST.get("address_id")

    if selected_address_id:

        selected_address = get_object_or_404(
            Address,
            id=selected_address_id,
            user=request.user,
        )

    else:

        selected_address = addresses.filter(
            is_default=True
        ).first()

    # -------------------------------------------------
    # PLACE ORDER
    # -------------------------------------------------

    if request.method == "POST" and request.POST.get("place_order"):

        if not selected_address:

            messages.error(
                request,
                "Please select a delivery address.",
            )

            return redirect("checkout")

        with transaction.atomic():

            # Re-fetch cart items inside the transaction
            order_items = list(
                cart.items.select_related(
                    "variant",
                    "variant__product",
                    "variant__inventory",
                )
            )

            if not order_items:

                messages.warning(
                    request,
                    "Your cart is empty.",
                )

                return redirect("cart_detail")

            subtotal = Decimal("0.00")

            # -----------------------------------------
            # CHECK STOCK + CALCULATE SUBTOTAL
            # -----------------------------------------

            for item in order_items:

                inventory = item.variant.inventory

                if item.quantity > inventory.quantity:

                    messages.error(
                        request,
                        f"Not enough stock available for "
                        f"{item.variant.product.name}.",
                    )

                    return redirect("cart_detail")

                subtotal += (
                    item.unit_price * item.quantity
                )

            # -----------------------------------------
            # COUPON
            # -----------------------------------------

            coupon, discount = get_applied_coupon(
                request,
                subtotal,
            )

            final_total = calculate_final_total(
                subtotal,
                discount,
            )

            delivery_fee = Decimal("0.00")

            final_total += delivery_fee

            # -----------------------------------------
            # CREATE ORDER
            # -----------------------------------------

            order = Order.objects.create(
                user=request.user,
                address=selected_address,
                status="pending",
                delivery_method="delivery",
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=final_total,
            )

            # -----------------------------------------
            # CREATE ORDER ITEMS
            # -----------------------------------------

            for item in order_items:

                variant = item.variant

                OrderItem.objects.create(
                    order=order,
                    variant=variant,
                    product_name=variant.product.name,
                    variant_name=variant.name,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    subtotal=item.unit_price * item.quantity,
                )

                # -------------------------------------
                # REDUCE INVENTORY
                # -------------------------------------

                inventory = variant.inventory

                inventory.quantity -= item.quantity

                inventory.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )

            # -----------------------------------------
            # CLEAR CART
            # -----------------------------------------

            cart.items.all().delete()

        # ---------------------------------------------
        # CLEAR APPLIED COUPON FROM SESSION
        # ---------------------------------------------

        request.session.pop(
            "coupon_id",
            None,
        )

        request.session.pop(
            "coupon_code",
            None,
        )

        request.session.pop(
            "coupon_discount",
            None,
        )

        request.session.modified = True

        messages.success(
            request,
            f"Order #{order.id} placed successfully!",
        )

        return redirect(
            "order_detail",
            order_id=order.id,
        )

    # -------------------------------------------------
    # CHECKOUT DISPLAY
    # -------------------------------------------------

    subtotal = Decimal("0.00")

    for item in items:

        subtotal += (
            item.unit_price * item.quantity
        )

    coupon, discount = get_applied_coupon(
        request,
        subtotal,
    )

    final_total = calculate_final_total(
        subtotal,
        discount,
    )

    delivery_fee = Decimal("0.00")

    final_total += delivery_fee

    return render(
        request,
        "checkout/checkout.html",
        {
            "cart": cart,
            "items": items,
            "addresses": addresses,
            "selected_address": selected_address,
            "subtotal": subtotal,
            "coupon": coupon,
            "discount": discount,
            "delivery_fee": delivery_fee,
            "final_total": final_total,
        },
    )