from __future__ import annotations
import tempfile
from typing import Any
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from shop.forms import OrderForm
from shop.models import Category, Drone, Order


def _fake_image_file(name: str = "test.jpg") -> SimpleUploadedFile:
    #повертає маленький несправжній файл зображення.
    return SimpleUploadedFile(
        name=name,
        content=b"\x47\x49\x46\x38\x39\x61",  #мінімальний заголовок GIF
        content_type="image/gif",
    )


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ShopClientTestSuite(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        #спільні дані, створені один раз для всього класу тестів.
        cls.user = User.objects.create_user(
            username="alice",
            email="alice@example.com",
            password="StrongPass123!",
        )
        cls.other_user = User.objects.create_user(
            username="bob",
            email="bob@example.com",
            password="StrongPass123!",
        )

        cls.category = Category.objects.create(name="Recon")

        cls.drone = Drone.objects.create(
            name="DJI-Test",
            model="X1",
            category=cls.category,
            price=1000,
            quantity=1,
            image=_fake_image_file(),
            specifications="Specs",
            manufacturer="Maker",
        )

    #A)тести моделей


    def test_category_str_returns_name(self) -> None:
        #category.__str__ має повертати назву категорії
        self.assertEqual(str(self.category), "Recon")

    def test_drone_str_returns_name(self) -> None:
        #drone.__str__ має повертати назву дрона
        self.assertEqual(str(self.drone), "DJI-Test")

    def test_order_str_returns_string(self) -> None:
        #order.__str__ має повертати рядок
        order = Order.objects.create(
            client=self.user,
            drone=self.drone,
            country="Ukraine",
            city="Kyiv",
            address="Main st",
            number_of_phone=123456789,
        )
        self.assertIsInstance(str(order), str)

    def test_order_default_country_is_ukraine(self) -> None:
        #order.country має бути 'Ukraine' якщо не вказано інше
        order = Order.objects.create(
            client=self.user,
            drone=self.drone,
            city="Kyiv",
            address="Main st",
            number_of_phone=123456789,
        )
        self.assertEqual(order.country, "Ukraine")

    def test_order_foreign_keys_link_user_and_drone(self) -> None:
        #замовлення має посилатися на конкретного користувача та конкретний дрон
        order = Order.objects.create(
            client=self.user,
            drone=self.drone,
            country="Poland",
            city="Warsaw",
            address="Street 1",
            number_of_phone=111222333,
        )
        self.assertEqual(order.client_id, self.user.id)
        self.assertEqual(order.drone_id, self.drone.id)

    def test_drone_belongs_to_category(self) -> None:
        #drone.category має вказувати на правильний запис категорії
        self.assertEqual(self.drone.category_id, self.category.id)


    def test_order_form_valid_with_correct_data(self) -> None:
        #orderForm має бути валідною з коректними даними
        form = OrderForm(
            data={
                "country": "Ukraine",
                "city": "Kyiv",
                "address": "Main st",
                "number_of_phone": 123456789,
            }
        )
        self.assertTrue(form.is_valid())

    def test_order_form_invalid_missing_city(self) -> None:
        #orderForm має бути невалідною, якщо відсутнє місто
        form = OrderForm(
            data={
                "country": "Ukraine",
                "address": "Main st",
                "number_of_phone": 123456789,
            }
        )
        self.assertFalse(form.is_valid())

    def test_order_form_invalid_missing_address(self) -> None:
        #orderForm має бути невалідною, якщо відсутня адреса
        form = OrderForm(
            data={
                "country": "Ukraine",
                "city": "Kyiv",
                "number_of_phone": 123456789,
            }
        )
        self.assertFalse(form.is_valid())

    def test_order_form_invalid_missing_phone(self) -> None:
        #orderForm має бути невалідною, якщо відсутній телефон
        form = OrderForm(
            data={
                "country": "Ukraine",
                "city": "Kyiv",
                "address": "Main st",
            }
        )
        self.assertFalse(form.is_valid())

    def test_order_form_excludes_client_drone_date(self) -> None:
        #orderForm не повинна містити поля client/drone/date (вони встановлюються у view)
        form = OrderForm()
        self.assertNotIn("client", form.fields)
        self.assertNotIn("drone", form.fields)
        self.assertNotIn("date", form.fields)


    def test_home_view_returns_200(self) -> None:
        #головна сторінка має повертати код 200
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)

    def test_product_view_returns_200(self) -> None:
        #сторінка списку товарів має повертати код 200
        resp = self.client.get(reverse("product"))
        self.assertEqual(resp.status_code, 200)

    def test_product_view_contains_drones_in_context(self) -> None:
        #сторінка товарів має містити дронів у контексті шаблону
        resp = self.client.get(reverse("product"))
        self.assertIn("drones", resp.context)
        self.assertTrue(any(d.id == self.drone.id for d in resp.context["drones"]))

    def test_detail_view_returns_200(self) -> None:
        #детальна сторінка дрона має повертати код 200
        resp = self.client.get(reverse("detail", args=[self.drone.id]))
        self.assertEqual(resp.status_code, 200)

    def test_detail_view_contains_form_and_drone(self) -> None:
        #детальна сторінка дрона має передавати 'drone' та 'form' у контекст
        resp = self.client.get(reverse("detail", args=[self.drone.id]))
        self.assertIn("drone", resp.context)
        self.assertIn("form", resp.context)
        self.assertEqual(resp.context["drone"].id, self.drone.id)

    #-------------------------
    #D) Тести створення замовлення + власності (3 тести)
    #-------------------------

    def test_anonymous_user_cannot_create_order(self) -> None:
        #POST-запит від аноніма НЕ повинен створювати замовлення
        before = Order.objects.count()
        resp = self.client.post(
            reverse("detail", args=[self.drone.id]),
            data={
                "country": "Ukraine",
                "city": "Kyiv",
                "address": "Main st",
                "number_of_phone": 123456789,
            },
        )
        after = Order.objects.count()

        self.assertEqual(before, after)
        #чкщо додати login_required, буде редірект 302 на логін
        self.assertEqual(resp.status_code, 302)

    def test_authenticated_user_can_create_order(self) -> None:
        #POST-запит авторизованого юзера має створювати Order, прив'язаний до нього та дрона
        self.client.login(username="alice", password="StrongPass123!")
        resp = self.client.post(
            reverse("detail", args=[self.drone.id]),
            data={
                "country": "Ukraine",
                "city": "Kyiv",
                "address": "Main st",
                "number_of_phone": 123456789,
            },
            follow=False,
        )
        self.assertEqual(resp.status_code, 302)  #ваш view перенаправляє на home
        self.assertTrue(
            Order.objects.filter(client=self.user, drone=self.drone).exists()
        )

    def test_user_orders_page_shows_only_own_orders(self) -> None:
        #сторінка замовлень має показувати лише замовлення залогіненого юзера.
        #створюємо по одному замовленню для кожного користувача
        Order.objects.create(
            client=self.user,
            drone=self.drone,
            country="Ukraine",
            city="Kyiv",
            address="A",
            number_of_phone=1,
        )
        Order.objects.create(
            client=self.other_user,
            drone=self.drone,
            country="Poland",
            city="Warsaw",
            address="B",
            number_of_phone=2,
        )

        self.client.login(username="alice", password="StrongPass123!")
        resp = self.client.get(reverse("orders"))
        self.assertEqual(resp.status_code, 200)

        orders = resp.context.get("orders", [])
        self.assertTrue(all(o.client_id == self.user.id for o in orders))



    def test_register_creates_user_and_redirects_home(self) -> None:
        #view реєстрації має створювати юзера і перенаправляти на home.
        before = User.objects.count()
        resp = self.client.post(
            reverse("register"),
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
            follow=False,
        )
        after = User.objects.count()

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(after, before + 1)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_login_then_logout_flow(self) -> None:
        #вхід має працювати, а вихід — перенаправляти на сторінку входу.
        resp_login = self.client.post(
            reverse("login"),
            data={"username": "alice", "password": "StrongPass123!"},
            follow=False,
        )
        self.assertEqual(resp_login.status_code, 302)

        resp_logout = self.client.get(reverse("logout"), follow=False)
        self.assertEqual(resp_logout.status_code, 302)
