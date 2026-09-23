from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Product, Category, Brand


def home(request):
    featured_products = (
        Product.objects
        .filter(
            is_active=True,
            is_featured=True
        )
        .select_related(
            "category",
            "brand"
        )
        .prefetch_related(
            "images",
            "variants__inventory"
        )[:8]
    )

    return render(
        request,
        "home/index.html",
        {
            "featured_products": featured_products
        }
    )


def product_list(request):
    products = (
        Product.objects
        .filter(is_active=True)
        .select_related(
            "category",
            "brand"
        )
        .prefetch_related(
            "images",
            "variants__inventory"
        )
    )

    # Search
    search_query = request.GET.get("q", "").strip()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(brand__name__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    # Category filter
    category_slug = request.GET.get("category", "").strip()

    if category_slug:
        products = products.filter(
            category__slug=category_slug
        )

    # Brand filter
    brand_slug = request.GET.get("brand", "").strip()

    if brand_slug:
        products = products.filter(
            brand__slug=brand_slug
        )

    # Price filter
    min_price = request.GET.get("min_price", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if min_price:
        products = products.filter(
            base_price__gte=min_price
        )

    if max_price:
        products = products.filter(
            base_price__lte=max_price
        )

    # Sorting
    sort = request.GET.get("sort", "").strip()

    if sort == "price_low":
        products = products.order_by("base_price")

    elif sort == "price_high":
        products = products.order_by("-base_price")

    elif sort == "name":
        products = products.order_by("name")

    else:
        products = products.order_by("-created_at")

    # Pagination
    paginator = Paginator(products, 12)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    categories = Category.objects.filter(
        is_active=True
    )

    brands = Brand.objects.filter(
        is_active=True
    )

    context = {
        "page_obj": page_obj,
        "categories": categories,
        "brands": brands,
        "search_query": search_query,
    }

    return render(
        request,
        "store/product_list.html",
        context
    )


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects
        .select_related(
            "category",
            "brand"
        )
        .prefetch_related(
            "images",
            "variants__inventory"
        ),
        slug=slug,
        is_active=True
    )

    return render(
        request,
        "store/product_detail.html",
        {
            "product": product
        }
    )