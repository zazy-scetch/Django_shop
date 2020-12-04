from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Case, DecimalField, F, IntegerField, Q, When

from adminapp.views import db_profile_by_type
from mainapp.models import Product
from ordersapp.models import OrderItem


class Command(BaseCommand):
    def handle(self, *args, **options):
        # test_products = Product.objects.filter(Q(category__name="офис") | Q(category__name="модерн")).select_related()
        # print(len(test_products))
        # print(test_products.count())
        # print(test_products)
        # db_profile_by_type("learn db", "", connection.queries)

        # Number of sale
        ACTION_1 = 1
        ACTION_2 = 2
        ACTION_EXPIRED = 3

        # Period of sale
        action_1__time_delta = timedelta(hours=12)
        action_2__time_delta = timedelta(days=1)

        # Discount amount
        action_1__discount = 0.3
        action_2__discount = 0.15
        action_expired__discount = 0.05

        # Conditions of sale: returns True or False of condition.
        # F objects means that all calculation will be in database with SQL query
        action_1__condition = Q(order__updated__lte=F("order__created") + action_1__time_delta)
        action_2__condition = Q(order__updated__gt=F("order__created") + action_1__time_delta) & Q(
            order__updated__lte=F("order__created") + action_2__time_delta
        )
        action_expired__condition = Q(order__updated__gt=F("order__created") + action_2__time_delta)

        # Condition mapping with number of sale: when Q object returns True, then return number of sale
        action_1__order = When(action_1__condition, then=ACTION_1)
        action_2__order = When(action_2__condition, then=ACTION_2)
        action_expired__order = When(action_expired__condition, then=ACTION_EXPIRED)

        # Condition mapping with discount: when Q object returns True, then calculate discount
        # Second 'when' with '-' for decrease ordering
        # F objects means that all calculation will be in database with SQL query
        action_1__price = When(action_1__condition, then=F("product__price") * F("quantity") * action_1__discount)
        action_2__price = When(action_2__condition, then=F("product__price") * F("quantity") * -action_2__discount)
        action_expired__price = When(
            action_expired__condition, then=F("product__price") * F("quantity") * action_expired__discount
        )

        # First: we need to annotate every object of OrderItem model with virtual field with number of sale
        # Second: we need to annotate every object of OrderItem model with virtual field with value of discount
        test_orders = (
            OrderItem.objects.annotate(
                action_order=Case(
                    action_1__order,
                    action_2__order,
                    action_expired__order,
                    output_field=IntegerField(),
                )
            )
            .annotate(
                total_discount=Case(
                    action_1__price,
                    action_2__price,
                    action_expired__price,
                    output_field=DecimalField(),
                )
            )
            .order_by("action_order", "total_discount")
            .select_related()
        )

        for orderitem in test_orders:
            print(
                f"{orderitem.action_order:2}: заказ №{orderitem.pk:3}: {orderitem.product.name:15}: скидка {abs(orderitem.total_discount):9.2f} руб. | {orderitem.order.updated - orderitem.order.created}"
            )
