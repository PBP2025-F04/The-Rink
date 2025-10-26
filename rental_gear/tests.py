from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from .models import Gear, CartItem, Rental, RentalItem
from .forms import GearForm, AddToCartForm, CheckoutForm
from authentication.models import UserType
import json

class GearModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='seller', password='pass')
        self.gear = Gear.objects.create(
            name='Test Gear',
            category='hockey',
            price_per_day=10.00,
            stock=5,
            seller=self.user
        )

    def test_gear_str(self):
        self.assertEqual(str(self.gear), 'Test Gear')

    def test_gear_creation(self):
        self.assertEqual(self.gear.name, 'Test Gear')
        self.assertEqual(self.gear.category, 'hockey')
        self.assertEqual(self.gear.price_per_day, 10.00)
        self.assertEqual(self.gear.stock, 5)
        self.assertEqual(self.gear.seller, self.user)

class CartItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.gear = Gear.objects.create(
            name='Test Gear',
            category='hockey',
            price_per_day=10.00,
            stock=5,
            seller=User.objects.create_user(username='seller', password='pass')
        )
        self.cart_item = CartItem.objects.create(
            user=self.user,
            gear=self.gear,
            quantity=2,
            days=3
        )

    def test_get_total_price(self):
        expected = 10.00 * 2 * 3  # 60.00
        self.assertEqual(self.cart_item.get_total_price(), expected)

class RentalModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='pass')
        self.rental = Rental.objects.create(
            customer_name='Test Customer',
            user=self.user,
            return_date=timezone.now().date() + timezone.timedelta(days=7),
            total_cost=100.00
        )

    def test_rental_creation(self):
        self.assertEqual(self.rental.customer_name, 'Test Customer')
        self.assertEqual(self.rental.user, self.user)
        self.assertEqual(self.rental.total_cost, 100.00)

class RentalItemModelTest(TestCase):
    def setUp(self):
        self.rental = Rental.objects.create(
            customer_name='Test Customer',
            return_date=timezone.now().date() + timezone.timedelta(days=7),
            total_cost=100.00
        )
        self.rental_item = RentalItem.objects.create(
            rental=self.rental,
            gear_name='Test Gear',
            quantity=2,
            price_per_day_at_checkout=10.00
        )

    def test_get_subtotal(self):
        expected = 10.00 * 2  # 20.00
        self.assertEqual(self.rental_item.get_subtotal(), expected)

class GearFormTest(TestCase):
    def test_gear_form_valid(self):
        form_data = {
            'name': 'Test Gear',
            'category': 'hockey',
            'price_per_day': 10.00,
            'image_url': 'http://example.com/image.jpg',
            'description': 'Test description',
            'stock': 5
        }
        form = GearForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_gear_form_invalid(self):
        form_data = {
            'name': '',
            'category': 'invalid',
            'price_per_day': -10.00,
            'stock': -1
        }
        form = GearForm(data=form_data)
        self.assertFalse(form.is_valid())

class AddToCartFormTest(TestCase):
    def test_add_to_cart_form_valid(self):
        form_data = {'quantity': 2, 'days': 5}
        form = AddToCartForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_add_to_cart_form_invalid_quantity(self):
        form_data = {'quantity': 0, 'days': 5}
        form = AddToCartForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_add_to_cart_form_invalid_days(self):
        form_data = {'quantity': 2, 'days': 35}
        form = AddToCartForm(data=form_data)
        self.assertFalse(form.is_valid())

class CheckoutFormTest(TestCase):
    def test_checkout_form_valid(self):
        form_data = {'customer_name': 'Test Customer'}
        form = CheckoutForm(data=form_data)
        self.assertTrue(form.is_valid())

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.seller = User.objects.create_user(username='seller', password='pass')
        UserType.objects.create(user=self.seller, user_type='seller')
        self.user = User.objects.create_user(username='user', password='pass')
        self.gear = Gear.objects.create(
            name='Test Gear',
            category='hockey',
            price_per_day=10.00,
            stock=5,
            seller=self.seller
        )

    def test_catalog_view(self):
        response = self.client.get(reverse('rental_gear:catalog'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog.html')

    def test_gear_detail_view(self):
        response = self.client.get(reverse('rental_gear:gear_detail', args=[self.gear.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gear_detail.html')

    def test_gear_detail_ajax_view(self):
        response = self.client.get(reverse('rental_gear:gear_detail', args=[self.gear.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Test Gear')

    def test_create_gear_view_get(self):
        self.client.login(username='seller', password='pass')
        response = self.client.get(reverse('rental_gear:create_gear'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rental_gear/gear_form.html')

    def test_create_gear_view_post_valid(self):
        self.client.login(username='seller', password='pass')
        form_data = {
            'name': 'New Gear',
            'category': 'curling',
            'price_per_day': 15.00,
            'image_url': 'http://example.com/new.jpg',
            'description': 'New gear',
            'stock': 3
        }
        response = self.client.post(reverse('rental_gear:create_gear'), form_data)
        self.assertRedirects(response, reverse('rental_gear:catalog'))
        self.assertTrue(Gear.objects.filter(name='New Gear').exists())

    def test_create_gear_view_post_invalid(self):
        self.client.login(username='seller', password='pass')
        form_data = {'name': '', 'category': 'hockey', 'price_per_day': 10.00, 'stock': 5}
        response = self.client.post(reverse('rental_gear:create_gear'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rental_gear/gear_form.html')

    def test_update_gear_view_get(self):
        self.client.login(username='seller', password='pass')
        response = self.client.get(reverse('rental_gear:update_gear', args=[self.gear.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rental_gear/gear_form.html')

    def test_update_gear_view_post_valid(self):
        self.client.login(username='seller', password='pass')
        form_data = {
            'name': 'Updated Gear',
            'category': 'hockey',
            'price_per_day': 12.00,
            'image_url': 'http://example.com/updated.jpg',
            'description': 'Updated',
            'stock': 4
        }
        response = self.client.post(reverse('rental_gear:update_gear', args=[self.gear.id]), form_data)
        self.assertRedirects(response, reverse('rental_gear:catalog'))
        self.gear.refresh_from_db()
        self.assertEqual(self.gear.name, 'Updated Gear')

    def test_update_gear_ajax_post_valid(self):
        self.client.login(username='seller', password='pass')
        form_data = {
            'name': 'Updated Gear',
            'category': 'hockey',
            'price_per_day': 12.00,
            'image_url': 'http://example.com/updated.jpg',
            'description': 'Updated',
            'stock': 4
        }
        response = self.client.post(reverse('rental_gear:update_gear', args=[self.gear.id]), form_data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_delete_gear_view_get(self):
        self.client.login(username='seller', password='pass')
        response = self.client.get(reverse('rental_gear:delete_gear', args=[self.gear.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'rental_gear/gear_confirm_delete.html')

    def test_delete_gear_view_post(self):
        self.client.login(username='seller', password='pass')
        response = self.client.post(reverse('rental_gear:delete_gear', args=[self.gear.id]))
        self.assertRedirects(response, reverse('rental_gear:catalog'))
        self.assertFalse(Gear.objects.filter(id=self.gear.id).exists())

    def test_delete_gear_ajax_post(self):
        self.client.login(username='seller', password='pass')
        response = self.client.post(reverse('rental_gear:delete_gear', args=[self.gear.id]), HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])

    def test_filter_gear_view(self):
        response = self.client.get(reverse('rental_gear:filter_gear'), {'category': 'hockey'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/gear_items.html')

    def test_view_cart_view(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('rental_gear:view_cart'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cart.html')

    def test_add_to_cart_view(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('rental_gear:add_to_cart', args=[self.gear.id]), json.dumps({'quantity': 1, 'days': 2}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/cart_items.html')
        self.assertTrue(CartItem.objects.filter(user=self.user, gear=self.gear).exists())

    def test_remove_from_cart_view(self):
        self.client.login(username='user', password='pass')
        cart_item = CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.post(reverse('rental_gear:remove_from_cart', args=[cart_item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/cart_items.html')
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_checkout_view_get(self):
        self.client.login(username='user', password='pass')
        CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.get(reverse('rental_gear:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout.html')

    def test_checkout_view_post(self):
        self.client.login(username='user', password='pass')
        CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.post(reverse('rental_gear:checkout'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'checkout_success.html')
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())

    def test_checkout_view_empty_cart(self):
        self.client.login(username='user', password='pass')
        response = self.client.get(reverse('rental_gear:checkout'))
        self.assertRedirects(response, reverse('rental_gear:view_cart'))

    def test_add_to_cart_ajax_authenticated(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('rental_gear:add_to_cart_ajax', args=[self.gear.id]), json.dumps({'quantity': 1, 'days': 2}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertTrue(CartItem.objects.filter(user=self.user, gear=self.gear).exists())

    def test_add_to_cart_ajax_not_authenticated(self):
        response = self.client.post(reverse('rental_gear:add_to_cart_ajax', args=[self.gear.id]), json.dumps({'quantity': 1, 'days': 2}), content_type='application/json')
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertTrue(data['login_required'])

    def test_add_to_cart_ajax_invalid_days(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('rental_gear:add_to_cart_ajax', args=[self.gear.id]), {'quantity': 1, 'days': 35})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_remove_from_cart_ajax_authenticated(self):
        self.client.login(username='user', password='pass')
        cart_item = CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.post(reverse('rental_gear:remove_from_cart_ajax', args=[cart_item.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())

    def test_remove_from_cart_ajax_not_authenticated(self):
        cart_item = CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.post(reverse('rental_gear:remove_from_cart_ajax', args=[cart_item.id]))
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertTrue(data['login_required'])

    def test_checkout_ajax_authenticated(self):
        self.client.login(username='user', password='pass')
        CartItem.objects.create(user=self.user, gear=self.gear, quantity=1, days=1)
        response = self.client.post(reverse('rental_gear:checkout_ajax'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.assertTrue(Rental.objects.filter(user=self.user).exists())

    def test_checkout_ajax_not_authenticated(self):
        response = self.client.post(reverse('rental_gear:checkout_ajax'))
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_checkout_ajax_empty_cart(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(reverse('rental_gear:checkout_ajax'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])

    def test_gear_json_view(self):
        self.client.login(username='seller', password='pass')
        response = self.client.get(reverse('rental_gear:gear_json', args=[self.gear.id]))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'Test Gear')
