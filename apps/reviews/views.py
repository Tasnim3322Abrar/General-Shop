from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

from apps.orders.models import OrderItem
from apps.store.models import Product

from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_active=True,
    )

    # Check whether the user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        variant__product=product,
        order__status__in=[
            "confirmed",
            "processing",
            "shipped",
            "delivered",
        ],
    ).exists()

    if not has_purchased:
        messages.error(
            request,
            "You can only review products that you have purchased.",
        )
        return redirect("product_detail", slug=product.slug)

    # Prevent duplicate reviews
    existing_review = Review.objects.filter(
        product=product,
        user=request.user,
    ).first()

    if existing_review:
        messages.error(
            request,
            "You have already reviewed this product.",
        )
        return redirect("product_detail", slug=product.slug)

    if request.method != "POST":
        return redirect("product_detail", slug=product.slug)

    form = ReviewForm(request.POST)

    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        messages.success(
            request,
            "Your review has been submitted successfully.",
        )
    else:
        messages.error(
            request,
            "Please correct the review form.",
        )

    return redirect("product_detail", slug=product.slug)