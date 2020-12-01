from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from mainapp.models import Product


class Basket(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="basket")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="количество", default=0)
    add_datetime = models.DateTimeField(verbose_name="время добавления", auto_now_add=True)

    @property
    def product_cost(self):
        "return cost of all products this type"
        return self.product.price * self.quantity

    @property
    def total_quantity(self):
        "return total quantity for user"
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.quantity, _items)))

    @property
    def total_cost(self):
        "return total cost for user"
        _items = self.get_items_cached
        return sum(list(map(lambda x: x.product_cost, _items)))

    @staticmethod
    def get_item(pk):
        return get_object_or_404(Basket, pk=pk)

    # @staticmethod
    # def get_items(user):
    #     return Basket.objects.filter(user=user).order_by("product__category")

    @cached_property
    def get_items_cached(self):
        return self.user.basket.select_related()