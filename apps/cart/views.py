from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.shortcuts import render

from apps.store.models import ProductVariant

from .models import CartItem
from .services import get_or_create_cart


def cart_detail(request):

    cart = get_or_create_cart(request)

    items = (
        cart.items
        .select_related(
            "variant",
            "variant__product",
        )
        .prefetch_related(
            "variant__product__images",
        )
    )

    return render(
        request,
        "cart/cart_detail.html",
        {
            "cart": cart,
            "items": items,
        },
    )


def add_to_cart(request, variant_id):

    if request.method != "POST":

        return redirect("product_list")


    variant = get_object_or_404(
        ProductVariant.objects.select_related(
            "product",
            "inventory",
        ),
        id=variant_id,
        is_active=True,
    )


    if not variant.inventory.is_in_stock:

        messages.error(
            request,
            "This product is currently out of stock.",
        )

        return redirect(
            "product_detail",
            slug=variant.product.slug,
        )


    cart = get_or_create_cart(request)


    item, created = CartItem.objects.get_or_create(
        cart=cart,
        variant=variant,
        defaults={
            "quantity": 1,
        },
    )


    if not created:

        new_quantity = item.quantity + 1

        if new_quantity > variant.inventory.quantity:

            messages.error(
                request,
                "Not enough stock available.",
            )

            return redirect("cart_detail")


        item.quantity = new_quantity

        item.save(
            update_fields=[
                "quantity",
                "updated_at",
            ]
        )


    messages.success(
        request,
        f"{variant.product.name} added to your cart.",
    )

    return redirect("cart_detail")


def update_cart(request, item_id):

    if request.method != "POST":

        return redirect("cart_detail")


    cart = get_or_create_cart(request)


    item = get_object_or_404(
        CartItem.objects.select_related(
            "variant",
            "variant__inventory",
        ),
        id=item_id,
        cart=cart,
    )


    try:

        quantity = int(
            request.POST.get(
                "quantity",
                1,
            )
        )

    except (TypeError, ValueError):

        quantity = 1


    if quantity < 1:

        item.delete()

        messages.success(
            request,
            "Item removed from your cart.",
        )

        return redirect("cart_detail")


    if quantity > item.variant.inventory.quantity:

        messages.error(
            request,
            "Requested quantity exceeds available stock.",
        )

        return redirect("cart_detail")


    item.quantity = quantity

    item.save(
        update_fields=[
            "quantity",
            "updated_at",
        ]
    )


    messages.success(
        request,
        "Cart updated successfully.",
    )

    return redirect("cart_detail")


def remove_from_cart(request, item_id):

    if request.method != "POST":

        return redirect("cart_detail")


    cart = get_or_create_cart(request)


    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart,
    )


    item.delete()


    messages.success(
        request,
        "Item removed from your cart.",
    )

    return redirect("cart_detail")