from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.cart.services import get_or_create_cart

from .forms import AddressForm
from .models import Address
from .models import Order
from .models import OrderItem


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
    )

    if not items.exists():

        messages.error(
            request,
            "Your cart is empty.",
        )

        return redirect("cart_detail")


    addresses = Address.objects.filter(
        user=request.user
    )


    if request.method == "POST":

        form = AddressForm(request.POST)

        delivery_method = request.POST.get(
            "delivery_method",
            "delivery",
        )

        address_id = request.POST.get(
            "address_id"
        )


        if address_id:

            address = get_object_or_404(
                Address,
                id=address_id,
                user=request.user,
            )

        else:

            if not form.is_valid():

                return render(
                    request,
                    "orders/checkout.html",
                    {
                        "cart": cart,
                        "items": items,
                        "addresses": addresses,
                        "form": form,
                    },
                )

            address = form.save(
                commit=False
            )

            address.user = request.user
            address.save()


        if delivery_method == "delivery":

            delivery_fee = Decimal("60.00")

        else:

            delivery_fee = Decimal("0.00")


        subtotal = cart.subtotal

        total = subtotal + delivery_fee


        # Check stock before creating the order.

        for item in items:

            if (
                item.quantity
                > item.variant.inventory.quantity
            ):

                messages.error(
                    request,
                    f"Not enough stock for "
                    f"{item.variant.product.name}.",
                )

                return redirect(
                    "cart_detail"
                )


        with transaction.atomic():

            order = Order.objects.create(

                user=request.user,

                address=address,

                delivery_method=delivery_method,

                subtotal=subtotal,

                delivery_fee=delivery_fee,

                total=total,

            )


            for item in items:

                OrderItem.objects.create(

                    order=order,

                    variant=item.variant,

                    product_name=(
                        item.variant.product.name
                    ),

                    variant_name=item.variant.name,

                    quantity=item.quantity,

                    unit_price=item.variant.price,

                    subtotal=(
                        item.variant.price
                        * item.quantity
                    ),

                )


                inventory = (
                    item.variant.inventory
                )

                inventory.quantity -= item.quantity

                inventory.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )


            cart.items.all().delete()


        messages.success(
            request,
            "Your order has been placed successfully.",
        )

        return redirect(
            "order_confirmation",
            order_id=order.id,
        )


    else:

        form = AddressForm()


    return render(
        request,
        "orders/checkout.html",
        {
            "cart": cart,
            "items": items,
            "addresses": addresses,
            "form": form,
        },
    )

@login_required
def order_confirmation(request, order_id):

    order = get_object_or_404(
        Order.objects.prefetch_related(
            "items"
        ),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_confirmation.html",
        {
            "order": order,
        },
    )

@login_required
def order_list(request):

    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
    )

    return render(
        request,
        "orders/order_list.html",
        {
            "orders": orders,
        },
    )


@login_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects
        .prefetch_related("items")
        .select_related("address"),
        id=order_id,
        user=request.user,
    )

    return render(
        request,
        "orders/order_detail.html",
        {
            "order": order,
        },
    )