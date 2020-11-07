# Generated by Django 2.2.16 on 2020-11-07 11:22

from django.db import migrations, transaction


def forwards_func(apps, schema_editor):
    try:
        from authnapp.models import ShopUser, ShopUserProfile

        with transaction.atomic():
            qs = ShopUser.objects.all()
            for item in qs:
                ShopUserProfile.objects.create(user=item)
    except Exception as exp:
        print(f"Cann't create user profile: {exp}")


def reverse_func(apps, schema_editor):
    try:
        from authnapp.models import ShopUserProfile

        with transaction.atomic():
            ShopUserProfile.objects.all().delete()
    except Exception as exp:
        print(f"Cann't delete users profiles: {exp}")


class Migration(migrations.Migration):

    dependencies = [
        ("authnapp", "0004_user_profile"),
    ]

    operations = [migrations.RunPython(forwards_func, reverse_func)]
