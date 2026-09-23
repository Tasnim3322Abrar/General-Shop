from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "session_key",
        "created_at",
        "updated_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "session_key",
    )


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):

    list_display = (
        "cart",
        "variant",
        "quantity",
        "unit_price",
        "subtotal",
        "added_at",
    )

    list_filter = (
        "added_at",
    )

    search_fields = (
        "variant__product__name",
        "variant__sku",
    )