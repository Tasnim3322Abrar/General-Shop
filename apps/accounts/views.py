from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(request, user)

            messages.success(
                request,
                "Your account has been created successfully."
            )

            return redirect("account")

    else:
        form = RegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


def login_view(request):
    if request.user.is_authenticated:
        return redirect("account")

    if request.method == "POST":
        from django.contrib.auth import authenticate

        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                "You have been logged in."
            )

            next_url = request.GET.get("next")

            if next_url:
                return redirect(next_url)

            return redirect("account")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "accounts/login.html"
    )


@login_required
def account(request):
    return render(
        request,
        "accounts/account.html"
    )


def logout_view(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")