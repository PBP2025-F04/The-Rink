import datetime
import tempfile
import os
import shutil
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.db import IntegrityError
from .models import Arena, Booking, ArenaOpeningHours

# --- Persiapan Template Mock ---
# Ini penting untuk mencegah error 'TemplateDoesNotExist'
# karena environment test tidak punya akses ke file template asli.
TEMP_TEMPLATE_DIR = tempfile.mkdtemp()
os.makedirs(os.path.join(TEMP_TEMPLATE_DIR, 'partials'), exist_ok=True)

MOCK_TEMPLATES = {
    'base.html': '{% block content %}{% endblock %}{% block extra_js %}{% endblock %}',
    'show_arena.html': '{% extends "base.html" %}{% if user.is_superuser %}{% include "partials/add_arena_modal.html" %}{% endif %}',
    'arena_detail.html': '{% extends "base.html" %}{% csrf_token %}',
    'user_bookings.html': '{% extends "base.html" %}{% csrf_token %}{% for booking in bookings %}{% include "partials/_booking_row.html" %}{% endfor %}',
    'partials/slot_list.html': '{% for h in hourly_slots_data %}<div class="slot-{{ h.hour }}">{{ h.status }}-{{ h.is_user_booking }}</div>{% endfor %}',
    'partials/select_sport_modal.html': '<form>{% csrf_token %}</form>',
    'partials/_booking_row.html': '<tr id="booking-row-{{ booking.id }}"><td>{{ booking.status }}</td><td>{% if booking.status == "Booked" %}<button hx-post="..."></button>{% endif %}</td></tr>',
    'partials/add_arena_modal.html': '<form id="add-arena-form"></form>',
    'partials/delete_arena_modal.html': '<div id="deleteArenaModal"></div>'
}

for TPL_NAME, TPL_CONTENT in MOCK_TEMPLATES.items():
    with open(os.path.join(TEMP_TEMPLATE_DIR, TPL_NAME), 'w') as f:
        f.write(TPL_CONTENT)

@override_settings(TEMPLATES=[{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [TEMP_TEMPLATE_DIR],
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
        ],
        'loaders': [
            'django.template.loaders.filesystem.Loader',
        ],
    },
}])
class BaseViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_TEMPLATE_DIR)
        super().tearDownClass()

class ModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='pw')
        cls.arena = Arena.objects.create(
            name="Test Arena", 
            description="Desc", 
            capacity=50, 
            location="Test Location"
        )
        cls.test_date = timezone.now().date() + datetime.timedelta(days=7)

    def test_arena_str(self):
        self.assertEqual(str(self.arena), "Test Arena")

    def test_opening_hours_str(self):
        hours = ArenaOpeningHours.objects.create(
            arena=self.arena, 
            day=0, 
            open_time=datetime.time(9, 0), 
            close_time=datetime.time(17, 0)
        )
        expected_str = f"Test Arena - Senin: 09:00 - 17:00"
        self.assertEqual(str(hours), expected_str)

    def test_booking_str(self):
        booking = Booking.objects.create(
            arena=self.arena,
            user=self.user,
            date=self.test_date,
            start_hour=10,
            activity='ice_skating'
        )
        expected_str = f"testuser @ Test Arena on {self.test_date} (10:00)"
        self.assertEqual(str(booking), expected_str)

    def test_booking_unique_constraint(self):
        Booking.objects.create(
            arena=self.arena,
            user=self.user,
            date=self.test_date,
            start_hour=11
        )
        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                arena=self.arena,
                user=self.user,
                date=self.test_date,
                start_hour=11
            )

class ViewTests(BaseViewTests):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='bris', password='pw')
        cls.other_user = User.objects.create_user(username='other', password='pw')
        
        cls.arena = Arena.objects.create(name="Arena Utama", capacity=50, location="Jakarta")
        
        today = timezone.now().date()
        days_until_monday = (0 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        cls.future_monday = today + datetime.timedelta(days=days_until_monday)
        cls.future_tuesday = cls.future_monday + datetime.timedelta(days=1)
        cls.past_date = today - datetime.timedelta(days=10)

        cls.opening_hours_senin = ArenaOpeningHours.objects.create(
            arena=cls.arena, day=0, open_time='09:00', close_time='17:00'
        )
        cls.opening_hours_selasa = ArenaOpeningHours.objects.create(
            arena=cls.arena, day=1, open_time=None, close_time=None
        )
        
        cls.booked_slot_other = Booking.objects.create(
            arena=cls.arena, 
            user=cls.other_user, 
            date=cls.future_monday, 
            start_hour=10, 
            status='Booked', 
            activity='ice_hockey'
        )

    def setUp(self):
        self.client = Client()
        
        self.my_booking = Booking.objects.create(
            arena=self.arena, 
            user=self.user, 
            date=self.future_monday, 
            start_hour=12, 
            status='Booked', 
            activity='curling'
        )
        
        self.cancelled_slot = Booking.objects.create(
            arena=self.arena, 
            user=self.other_user, 
            date=self.future_monday, 
            start_hour=14, 
            status='Cancelled', 
            activity='ice_skating'
        )
        
        self.client.login(username='bris', password='pw')

    def test_show_arena_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('booking_arena:show_arena'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_my_bookings_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('booking_arena:user_booking_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_show_arena_authenticated(self):
        response = self.client.get(reverse('booking_arena:show_arena'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'show_arena.html')
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)

    def test_my_bookings_authenticated(self):
        response = self.client.get(reverse('booking_arena:user_booking_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_bookings.html')
        self.assertIn(self.my_booking, response.context['bookings'])

    def test_get_available_slots_logic(self):
        url = reverse('booking_arena:get_available_slots', args=[self.arena.id])
        response = self.client.get(url, {'date': self.future_monday.strftime('%Y-%m-%d')})
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/slot_list.html')
        
        self.assertContains(response, 'Available-False', msg="Jam 9 harus 'Available' dan bukan booking user")
        self.assertContains(response, 'Booked-False', msg="Jam 10 harus 'Booked' dan bukan booking user")
        self.assertContains(response, 'Booked-True', msg="Jam 12 harus 'Booked' dan booking user")
        self.assertContains(response, 'Available-False', msg="Jam 14 harus 'Available' (karena slot 'Cancelled' di-filter)")

    def test_get_available_slots_closed_day(self):
        url = reverse('booking_arena:get_available_slots', args=[self.arena.id])
        response = self.client.get(url, {'date': self.future_tuesday.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_closed_today'])

    def test_get_available_slots_invalid_date(self):
        url = reverse('booking_arena:get_available_slots', args=[self.arena.id])
        response = self.client.get(url, {'date': 'bukan-tanggal'})
        self.assertEqual(response.status_code, 400)

    def test_get_sport_modal_success(self):
        url = reverse('booking_arena:get_sport_modal', args=[self.arena.id, 9])
        response = self.client.get(url, {'date': self.future_monday.strftime('%Y-%m-%d')})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'partials/select_sport_modal.html')

    def test_create_booking_success(self):
        url = reverse('booking_arena:create_booking_hourly', args=[self.arena.id])
        data = {
            'date': self.future_monday.strftime('%Y-%m-%d'),
            'hour': 9,
            'activity': 'ice_skating'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Booking.objects.filter(
            arena=self.arena, date=self.future_monday, start_hour=9, user=self.user, status='Booked'
        ).exists())
        self.assertContains(response, 'Booked-True', msg="Slot jam 9 seharusnya jadi 'Booked-True' di response HTML")
        self.assertIn('HX-Trigger', response)
        
    def test_create_booking_fail_already_booked(self):
        url = reverse('booking_arena:create_booking_hourly', args=[self.arena.id])
        data = {
            'date': self.future_monday.strftime('%Y-%m-%d'),
            'hour': 10,
            'activity': 'ice_skating'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 409)
        self.assertContains(response, 'no longer available')

    def test_create_booking_fail_past_date(self):
        url = reverse('booking_arena:create_booking_hourly', args=[self.arena.id])
        data = {
            'date': self.past_date.strftime('%Y-%m-%d'),
            'hour': 9,
            'activity': 'ice_skating'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Cannot book past dates')

    def test_create_booking_recycle_cancelled_slot(self):
        url = reverse('booking_arena:create_booking_hourly', args=[self.arena.id])
        data = {
            'date': self.future_monday.strftime('%Y-%m-%d'),
            'hour': 14,
            'activity': 'curling'
        }
        
        self.assertEqual(self.cancelled_slot.user, self.other_user)
        self.assertEqual(self.cancelled_slot.status, 'Cancelled')

        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        
        self.cancelled_slot.refresh_from_db()
        self.assertEqual(self.cancelled_slot.status, 'Booked')
        self.assertEqual(self.cancelled_slot.user, self.user)
        self.assertEqual(self.cancelled_slot.activity, 'curling')
        self.assertContains(response, 'Booked-True')

    def test_cancel_booking_from_arena_page(self):
        url = reverse('booking_arena:cancel_booking', args=[self.my_booking.id])
        response = self.client.post(url + '?from=arena', HTTP_X_CSRFTOKEN='dummytoken')
        
        self.assertEqual(response.status_code, 200)
        
        self.my_booking.refresh_from_db()
        self.assertEqual(self.my_booking.status, 'Cancelled')
        
        self.assertTemplateUsed(response, 'partials/slot_list.html')
        self.assertContains(response, 'Available-False', msg="Slot jam 12 harusnya jadi 'Available'")
        self.assertIn('HX-Trigger', response)

    def test_cancel_booking_from_my_bookings_page(self):
        url = reverse('booking_arena:cancel_booking', args=[self.my_booking.id])
        response = self.client.post(url + '?from=my_bookings', HTTP_X_CSRFTOKEN='dummytoken')
        
        self.assertEqual(response.status_code, 200)
        
        self.my_booking.refresh_from_db()
        self.assertEqual(self.my_booking.status, 'Cancelled')
        
        self.assertTemplateUsed(response, 'partials/_booking_row.html')
        self.assertContains(response, 'Cancelled')
        self.assertNotContains(response, 'hx-post')
        self.assertIn('HX-Trigger', response)

    def test_cancel_booking_fail_not_owned(self):
        url = reverse('booking_arena:cancel_booking', args=[self.booked_slot_other.id])
        response = self.client.post(url + '?from=arena', HTTP_X_CSRFTOKEN='dummytoken')
        
        self.assertEqual(response.status_code, 403)
        
        self.booked_slot_other.refresh_from_db()
        self.assertEqual(self.booked_slot_other.status, 'Booked')

    def test_cancel_booking_fail_past_date(self):
        past_booking = Booking.objects.create(
            arena=self.arena, 
            user=self.user, 
            date=self.past_date, 
            start_hour=12, 
            status='Booked'
        )
        url = reverse('booking_arena:cancel_booking', args=[past_booking.id])
        response = self.client.post(url + '?from=my_bookings', HTTP_X_CSRFTOKEN='dummytoken')
        
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Cannot cancel past bookings')
        
    def test_cancel_booking_twice(self):
        url = reverse('booking_arena:cancel_booking', args=[self.my_booking.id])
        response1 = self.client.post(url + '?from=arena', HTTP_X_CSRFTOKEN='dummytoken')
        self.assertEqual(response1.status_code, 200)
        self.my_booking.refresh_from_db()
        self.assertEqual(self.my_booking.status, 'Cancelled')

        response2 = self.client.post(url + '?from=arena', HTTP_X_CSRFTOKEN='dummytoken')
        self.assertEqual(response2.status_code, 200)
        self.assertContains(response2, 'Available-False')

@override_settings(TEMPLATES=[{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [TEMP_TEMPLATE_DIR],
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
        ],
        'loaders': [
            'django.template.loaders.filesystem.Loader',
        ],
    },
}])
class AdminViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='bris', password='pw')
        cls.superuser = User.objects.create_superuser(username='admin', password='pw')
        cls.arena = Arena.objects.create(name="Arena Lama", capacity=10, location="Lama")

    def test_add_arena_fail_not_superuser(self):
        self.client.login(username='bris', password='pw')
        url = reverse('booking_arena:add_arena_ajax')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)
        
    def test_delete_arena_fail_not_superuser(self):
        self.client.login(username='bris', password='pw')
        url = reverse('booking_arena:delete_arena_ajax', args=[self.arena.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        
    def setUp(self):
        self.client = Client()
        self.client.login(username='admin', password='pw')

    def test_delete_arena_success(self):
        temp_arena = Arena.objects.create(name="Arena Hapus", capacity=1, location="Hapus")
        url = reverse('booking_arena:delete_arena_ajax', args=[temp_arena.id])
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertFalse(Arena.objects.filter(id=temp_arena.id).exists())

    def test_add_arena_with_formset_success(self):
        url = reverse('booking_arena:add_arena_ajax')
        
        arena_data = {
            'name': 'Arena Baru Keren',
            'description': 'Deskripsi baru',
            'capacity': 100,
            'location': 'Lokasi Baru',
            'img_url': 'https://google.com/img.png',
            'google_maps_url': 'https://google.com/maps'
        }
        
        formset_data = {
            'hours-TOTAL_FORMS': '7',
            'hours-INITIAL_FORMS': '0',
            'hours-MIN_NUM_FORMS': '0',
            'hours-MAX_NUM_FORMS': '7',
            'hours-0-day': '0',
            'hours-0-open_time': '09:00',
            'hours-0-close_time': '22:00',
            'hours-1-day': '1',
            'hours-1-open_time': '09:00',
            'hours-1-close_time': '22:00',
            'hours-2-day': '2',
            'hours-2-open_time': '',
            'hours-2-close_time': '',
            'hours-3-day': '3', 'hours-3-open_time': '', 'hours-3-close_time': '',
            'hours-4-day': '4', 'hours-4-open_time': '', 'hours-4-close_time': '',
            'hours-5-day': '5', 'hours-5-open_time': '', 'hours-5-close_time': '',
            'hours-6-day': '6', 'hours-6-open_time': '', 'hours-6-close_time': '',
        }
        
        data = {**arena_data, **formset_data}
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 200)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'success')
        self.assertEqual(json_response['arena']['name'], 'Arena Baru Keren')
        
        self.assertTrue(Arena.objects.filter(name='Arena Baru Keren').exists())
        new_arena = Arena.objects.get(name='Arena Baru Keren')
        self.assertEqual(new_arena.opening_hours_rules.count(), 7)
        senin = new_arena.opening_hours_rules.get(day=0)
        self.assertEqual(senin.open_time, datetime.time(9, 0))
        rabu = new_arena.opening_hours_rules.get(day=2)
        self.assertIsNone(rabu.open_time)

    def test_add_arena_fail_invalid_data(self):
        url = reverse('booking_arena:add_arena_ajax')
        
        arena_data = {
            'name': '', 
            'description': 'Deskripsi baru',
            'capacity': 100,
            'location': 'Lokasi Baru',
        }
        
        formset_data = {
            'hours-TOTAL_FORMS': '7', 'hours-INITIAL_FORMS': '0',
            'hours-0-day': '0', 'hours-1-day': '1', 'hours-2-day': '2',
            'hours-3-day': '3', 'hours-4-day': '4', 'hours-5-day': '5', 'hours-6-day': '6',
        }
        data = {**arena_data, **formset_data}

        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 400)
        json_response = response.json()
        self.assertEqual(json_response['status'], 'error')
        self.assertIn('Validasi gagal', json_response['message'])
        self.assertIn('name', json_response['errors'])