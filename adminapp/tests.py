from django.conf import settings
from django.test import TestCase
from django.test.client import Client

from authnapp.models import ShopUser


class TestUserManagement(TestCase):
    fixtures = [
        "mainapp/fixtures/categories.json",
        "mainapp/fixtures/products.json",
        "mainapp/fixtures/contact_locations.json",
        "authnapp/fixtures/admin_user.json",
    ]

    def setUp(self):
        self.client = Client()
        self.superuser = ShopUser.objects.create_superuser("django2", "django2@geekshop.local", "geekbrains")
        self.user = ShopUser.objects.create_user("tarantino", "tarantino@geekshop.local", "geekbrains")
        self.user_with__first_name = ShopUser.objects.create_user(
            "umaturman", "umaturman@geekshop.local", "geekbrains", first_name="Ума"
        )

    def test_user_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_anonymous)
        self.assertEqual(response.context["title"], "главная")
        self.assertNotContains(response, "Пользователь", status_code=200)
        # self.assertNotIn('Пользователь', response.content.decode())

        # Set user's data
        self.client.login(username="tarantino", password="geekbrains")

        # Log in
        response = self.client.get("/auth/login/")
        self.assertFalse(response.context["user"].is_anonymous)
        self.assertEqual(response.context["user"], self.user)

        # After log in
        response = self.client.get("/")
        self.assertContains(response, "Пользователь", status_code=200)
        self.assertEqual(response.context["user"], self.user)
        # self.assertIn('Пользователь', response.content.decode())

    # def test_user_with__first_name_login(self):
    #     self.client.login(username='umaturman', password='geekbrains')
    #
    #     self.client.get('/auth/login/')
    #
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn(self.user_with__first_name.first_name, response.content.decode())
    #
    # def test_superuser_login(self):
    #     self.client.login(username='django2', password='geekbrains')
    #
    #     response = self.client.get('/auth/login/')
    #     self.assertEqual(response.context['user'].is_superuser, True)
    #
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('админка', response.content.decode())

    def test_basket_login_redirect(self):
        # Test without log in. Must be redirect.
        response = self.client.get("/basket/")
        self.assertEqual(response.url, "/auth/login/?next=/basket/")
        self.assertEqual(response.status_code, 302)

        self.client.login(username="tarantino", password="geekbrains")

        response = self.client.get("/basket/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context["basket"]), [])
        self.assertEqual(response.context["user"], self.user)
        self.assertEqual(response.context["title"], "корзина")
        self.assertEqual(response.request["PATH_INFO"], "/basket/")
        self.assertIn("Ваша корзина, Пользователь", response.content.decode())

    def test_user_logout(self):
        # User's data
        self.client.login(username="tarantino", password="geekbrains")

        # Log in
        response = self.client.get("/auth/login/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_anonymous)

        # Log out
        response = self.client.get("/auth/logout/")
        self.assertEqual(response.status_code, 302)

        # After log out
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["user"].is_anonymous)
        self.assertEqual(response.context["title"], "главная")
        self.assertNotIn("Пользователь", response.content.decode())

    def test_user_register(self):
        response = self.client.get("/auth/register/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["title"], "регистрация")
        self.assertTrue(response.context["user"].is_anonymous)

        new_user_data = {
            "username": "samuel",
            "first_name": "Сэмюэл",
            "last_name": "Джексон",
            "password1": "geekbrains",
            "password2": "geekbrains",
            "email": "sumuel@geekshop.local",
            "age": "21",
        }

        # Create new user
        response = self.client.post("/auth/register/", data=new_user_data)
        self.assertEqual(response.status_code, 302)

        new_user = ShopUser.objects.get(username=new_user_data["username"])
        # print(new_user, new_user.activation_key)

        activation_url = f"{settings.DOMAIN_NAME}/auth/verify/{new_user_data['email']}/{new_user.activation_key}/"

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, 200)

        self.client.login(username=new_user_data["username"], password=new_user_data["password1"])

        # Log in
        response = self.client.get("/auth/login/")
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_anonymous)

        # Main page check
        response = self.client.get("/")
        self.assertContains(response, text=new_user_data["first_name"], status_code=200)

    def test_user_wrong_register(self):
        new_user_data = {
            "username": "teen",
            "first_name": "Мэри",
            "last_name": "Поппинс",
            "password1": "geekbrains",
            "password2": "geekbrains",
            "email": "merypoppins@geekshop.local",
            "age": "17",
        }

        response = self.client.post("/auth/register/", data=new_user_data)
        self.assertEqual(response.status_code, 200)
        # self.assertFormError(response, form, field, errors, msg_prefix='')
        self.assertFormError(response, "register_form", "age", "Вы слишком молоды!")
        self.assertIn("Вы слишком молоды!", response.content.decode())
