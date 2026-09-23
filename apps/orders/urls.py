from django.urls import path

from .views import (
    address_create,
    address_delete,
    address_list,
    address_set_default,
    address_update,
    checkout,
    order_confirmation,
    order_detail,
    order_list,
)


urlpatterns = [

    path(
        "checkout/",
        checkout,
        name="checkout",
    ),

    path(
        "addresses/",
        address_list,
        name="address_list",
    ),

    path(
        "addresses/add/",
        address_create,
        name="address_create",
    ),

    path(
        "addresses/<int:address_id>/edit/",
        address_update,
        name="address_update",
    ),

    path(
        "addresses/<int:address_id>/delete/",
        address_delete,
        name="address_delete",
    ),

    path(
        "addresses/<int:address_id>/default/",
        address_set_default,
        name="address_set_default",
    ),

    path(
        "confirmation/<int:order_id>/",
        order_confirmation,
        name="order_confirmation",
    ),
    path(
        "",
        order_list,
        name="order_list",
    ),

    path(
        "<int:order_id>/",
        order_detail,
        name="order_detail",
    ),



]