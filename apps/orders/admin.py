from django.contrib import admin

from .models import Address, Order, OrderItem


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "full_name",
        "phone",
        "city",
        "is_default",
        "created_at",
    )

    list_filter = (
        "city",
        "is_default",
    )

    search_fields = (
        "user__username",
        "user__email",
        "full_name",
        "phone",
        "city",
    )


class OrderItemInline(admin.TabularInline):

    model = OrderItem
    extra = 0
    readonly_fields = (
        "product_name",
        "variant_name",
        "quantity",
        "unit_price",
        "subtotal",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "status",
        "delivery_method",
        "subtotal",
        "delivery_fee",
        "total",
        "created_at",
    )

    list_filter = (
        "status",
        "delivery_method",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    inlines = [
        OrderItemInline,
    ]