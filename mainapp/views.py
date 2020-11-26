import random

from django.conf import settings
from django.core.cache import cache
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Contact, Product, ProductCategory


def get_links_menu():
    if settings.LOW_CACHE:
        key = "links_menu"
        links_menu = cache.get(key)
        if links_menu is None:
            # print(f'caching {key}')
            links_menu = ProductCategory.objects.filter(is_active=True)
            cache.set(key, links_menu)
        return links_menu
    else:
        return ProductCategory.objects.filter(is_active=True)


def get_category(pk):
    if settings.LOW_CACHE:
        key = f"category_{pk}"
        category = cache.get(key)
        if category is None:
            category = get_object_or_404(ProductCategory, pk=pk)
            cache.set(key, category)
        return category
    else:
        return get_object_or_404(ProductCategory, pk=pk)


def get_products():
    if settings.LOW_CACHE:
        key = "products"
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).select_related("category")
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).select_related("category")


def get_product(pk):
    if settings.LOW_CACHE:
        key = f"product_{pk}"
        product = cache.get(key)
        if product is None:
            product = get_object_or_404(Product, pk=pk)
            cache.set(key, product)
        return product
    else:
        return get_object_or_404(Product, pk=pk)


def get_products_orederd_by_price():
    if settings.LOW_CACHE:
        key = "products_orederd_by_price"
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(is_active=True, category__is_active=True).order_by("price")
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(is_active=True, category__is_active=True).order_by("price")


def get_products_in_category_orederd_by_price(pk):
    if settings.LOW_CACHE:
        key = f"products_in_category_orederd_by_price_{pk}"
        products = cache.get(key)
        if products is None:
            products = Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by(
                "price"
            )
            cache.set(key, products)
        return products
    else:
        return Product.objects.filter(category__pk=pk, is_active=True, category__is_active=True).order_by("price")


def main(request):
    title = "главная"
    products = get_products()[:3]
    content = {"title": title, "products": products, "media_url": settings.MEDIA_URL}
    return render(request, "mainapp/index.html", content)


# def get_hot_product():
#     products = Product.objects.filter(is_active=True, category__is_active=True)
#     return random.sample(list(products), 1)[0]


# def get_same_products(hot_product):
#     same_products = Product.objects.filter(category=hot_product.category, is_active=True).exclude(pk=hot_product.pk)[:3]
#     return same_products


def get_hot_product_list():
    products = get_products()
    hot_product = random.sample(list(products), 1)[0]
    hot_list = products.exclude(pk=hot_product.pk)[:3]
    return (hot_product, hot_list)


def products(request, pk=None, page=1):
    title = "продукты"
    links_menu = get_links_menu()

    if pk is not None:
        if str(pk) == str(0):
            category = {"pk": 0, "name": "все"}
            products = get_products_orederd_by_price()
        else:
            category = get_category(pk)
            products = get_products_in_category_orederd_by_price(pk)

        paginator = Paginator(products, 2)
        try:
            products_paginator = paginator.page(page)
        except PageNotAnInteger:
            products_paginator = paginator.page(1)
        except EmptyPage:
            products_paginator = paginator.page(paginator.num_pages)

        content = {
            "title": title,
            "links_menu": links_menu,
            "category": category,
            "products": products_paginator,
            "media_url": settings.MEDIA_URL,
        }
        return render(request, "mainapp/products_list.html", content)
    # hot_product = get_hot_product()
    # same_products = get_same_products(hot_product)
    hot_product, same_products = get_hot_product_list()
    content = {
        "title": title,
        "links_menu": links_menu,
        "same_products": same_products,
        "media_url": settings.MEDIA_URL,
        "hot_product": hot_product,
    }
    return render(request, "mainapp/products.html", content)


def product(request, pk):
    title = "продукты"
    content = {
        "title": title,
        "links_menu": get_links_menu(),
        "product": get_product(pk),
        "media_url": settings.MEDIA_URL,
    }
    return render(request, "mainapp/product.html", content)


def contact(request):
    title = "о нас"
    visit_date = timezone.now()
    locations = Contact.objects.all()
    content = {"title": title, "visit_date": visit_date, "locations": locations}
    return render(request, "mainapp/contact.html", content)