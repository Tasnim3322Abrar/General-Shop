from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render
from django.views.decorators.http import require_POST

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

    default_address = addresses.filter(
        is_default=True
    ).first()

    if request.method == "POST":

        form = AddressForm(request.POST)

        delivery_method = request.POST.get(
            "delivery_method",
            "delivery",
        )

        address_id = request.POST.get(
            "address_id"
        )

        # ---------------------------------
        # SELECT EXISTING ADDRESS
        # ---------------------------------

        if address_id:

            address = get_object_or_404(
                Address,
                id=address_id,
                user=request.user,
            )

        # ---------------------------------
        # CREATE NEW ADDRESS
        # ---------------------------------

        else:

            if not form.is_valid():

                return render(
                    request,
                    "orders/checkout.html",
                    {
                        "cart": cart,
                        "items": items,
                        "addresses": addresses,
                        "default_address": default_address,
                        "form": form,
                    },
                )

            address = form.save(
                commit=False
            )

            address.user = request.user

            # If this is the user's first address,
            # automatically make it default.
            if not addresses.exists():
                address.is_default = True

            elif address.is_default:

                Address.objects.filter(
                    user=request.user,
                    is_default=True,
                ).update(
                    is_default=False
                )

            address.save()

        # ---------------------------------
        # DELIVERY FEE
        # ---------------------------------

        if delivery_method == "delivery":
            delivery_fee = Decimal("60.00")
        else:
            delivery_fee = Decimal("0.00")

        subtotal = cart.subtotal

        total = subtotal + delivery_fee

        # ---------------------------------
        # STOCK VALIDATION
        # ---------------------------------

        for item in items:

            if item.quantity > item.variant.inventory.quantity:

                messages.error(
                    request,
                    f"Not enough stock for "
                    f"{item.variant.product.name}.",
                )

                return redirect(
                    "cart_detail"
                )

        # ---------------------------------
        # CREATE ORDER
        # ---------------------------------

        with transaction.atomic():

            order = Order.objects.create(
                user=request.user,
                address=address,
                delivery_method=delivery_method,
                subtotal=subtotal,
                delivery_fee=delivery_fee,
                total=total,
            )

            # ---------------------------------
            # CREATE ORDER ITEMS
            # ---------------------------------

            for item in items:

                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    product_name=item.variant.product.name,
                    variant_name=item.variant.name,
                    quantity=item.quantity,
                    unit_price=item.variant.price,
                    subtotal=(
                        item.variant.price
                        * item.quantity
                    ),
                )

                inventory = item.variant.inventory

                inventory.quantity -= item.quantity

                inventory.save(
                    update_fields=[
                        "quantity",
                        "updated_at",
                    ]
                )

            # ---------------------------------
            # CLEAR CART
            # ---------------------------------

            cart.items.all().delete()

        messages.success(
            request,
            "Your order has been placed successfully.",
        )

        return redirect(
            "order_confirmation",
            order_id=order.id,
        )

    # ---------------------------------
    # GET REQUEST
    # ---------------------------------

    form = AddressForm()

    return render(
        request,
        "orders/checkout.html",
        {
            "cart": cart,
            "items": items,
            "addresses": addresses,
            "default_address": default_address,
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

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)

    return render(
        request,
        "orders/address_list.html",
        {
            "addresses": addresses,
        },
    )


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)

        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            has_existing_addresses = Address.objects.filter(
                user=request.user
            ).exists()

            # First address automatically becomes default.
            if not has_existing_addresses:
                address.is_default = True

            # If user selected this address as default,
            # remove default status from other addresses.
            elif address.is_default:
                Address.objects.filter(
                    user=request.user,
                    is_default=True,
                ).update(is_default=False)

            address.save()

            messages.success(
                request,
                "Address added successfully.",
            )

            return redirect("address_list")

    else:
        form = AddressForm()

    return render(
        request,
        "orders/address_form.html",
        {
            "form": form,
            "page_title": "Add Address",
            "button_text": "Add Address",
        },
    )


@login_required
def address_update(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    if request.method == "POST":
        form = AddressForm(
            request.POST,
            instance=address,
        )

        if form.is_valid():
            address = form.save(commit=False)

            if address.is_default:
                Address.objects.filter(
                    user=request.user,
                    is_default=True,
                ).exclude(
                    id=address.id
                ).update(
                    is_default=False
                )

            address.save()

            messages.success(
                request,
                "Address updated successfully.",
            )

            return redirect("address_list")

    else:
        form = AddressForm(instance=address)

    return render(
        request,
        "orders/address_form.html",
        {
            "form": form,
            "page_title": "Edit Address",
            "button_text": "Save Changes",
        },
    )


@login_required
@require_POST
def address_delete(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    address.delete()

    messages.success(
        request,
        "Address deleted successfully.",
    )

    return redirect("address_list")


@login_required
@require_POST
def address_set_default(request, address_id):
    address = get_object_or_404(
        Address,
        id=address_id,
        user=request.user,
    )

    with transaction.atomic():
        Address.objects.filter(
            user=request.user,
            is_default=True,
        ).update(is_default=False)

        address.is_default = True
        address.save(
            update_fields=[
                "is_default",
                "updated_at",
            ]
        )

    messages.success(
        request,
        "Default address updated.",
    )

    return redirect("address_list")