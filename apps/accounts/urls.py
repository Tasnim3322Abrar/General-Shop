from django.urls import path

from .views import (
    account,
    login_view,
    logout_view,
    register,
)


urlpatterns = [
    path(
        "register/",
        register,
        name="register"
    ),

    path(
        "login/",
        login_view,
        name="login"
    ),

    path(
        "logout/",
        logout_view,
        name="logout"
    ),

    path(
        "account/",
        account,
        name="account"
    ),
]