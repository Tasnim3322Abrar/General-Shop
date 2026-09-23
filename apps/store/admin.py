from django.contrib import admin

from .models import (
    StoreSettings,
    Category,
    Brand,
    Product,
    ProductImage,
    ProductVariant,
    Inventory,
)


@admin.register(StoreSettings)
class StoreSettingsAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "currency",
        "delivery_enabled",
        "pickup_enabled",
        "updated_at",
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "brand",
        "base_price",
        "is_active",
        "is_featured",
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    list_filter = (
        "category",
        "brand",
        "is_active",
        "is_featured",
    )

    search_fields = (
        "name",
        "description",
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "is_primary",
        "created_at",
    )

    list_filter = ("is_primary",)


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = (
        "product",
        "name",
        "sku",
        "price",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "product__name",
        "sku",
    )


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = (
        "variant",
        "quantity",
        "low_stock_threshold",
        "is_low_stock",
        "is_in_stock",
    )