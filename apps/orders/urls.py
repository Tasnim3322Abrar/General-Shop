from django.urls import path

from .views import checkout
from .views import order_confirmation
from .views import order_list
from .views import order_detail


urlpatterns = [

    path(
        "checkout/",
        checkout,
        name="checkout",
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