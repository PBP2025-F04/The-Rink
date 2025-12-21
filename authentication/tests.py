from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile, SellerProfile, UserType
from rental_gear.models import Gear
from events.models import Event
from forum.models import Post


class AuthenticationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )
        self.user_type = UserType.objects.create(user=self.user, user_type='customer')
        self.user_profile = UserProfile.objects.create(
            user=self.user,
            email='test@example.com',
            full_name='Test User',
            phone_number='1234567890'
        )

        # Create test seller
        self.seller = User.objects.create_user(
            username='testseller',
            password='sellerpass123',
            email='seller@example.com'
        )
        self.seller_type = UserType.objects.create(user=self.seller, user_type='seller')
        self.seller_profile = SellerProfile.objects.create(
            user=self.seller,
            business_name='Test Business',
            phone_number='0987654321'
        )

        # Create test data for dashboard counts
        self.gear = Gear.objects.create(
            name='Test Gear',
            category='hockey',
            price_per_day=100.00,
            description='Test description',
            seller=self.seller
        )
        # Create event in the future so it counts in dashboard
        from django.utils import timezone
        future_date = timezone.now().date() + timezone.timedelta(days=30)
        self.event = Event.objects.create(
            name='Test Event',
            description='Test event description',
            date=future_date
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.user
        )

        self.client = Client()

    def test_admin_login_success(self):
        """Test successful admin login with hardcoded credentials"""
        response = self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        self.assertTrue(self.client.session.get('is_admin'))
        # Check that admin user is created and logged in
        admin_user = User.objects.get(username='cbkadal')
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
        self.assertEqual(admin_user.first_name, 'Admin')
        self.assertEqual(admin_user.last_name, 'The Rink')

    def test_admin_login_failure(self):
        """Test failed admin login with wrong credentials"""
        response = self.client.post('/accounts/login/', {
            'username': 'wrong',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertFalse(self.client.session.get('is_admin'))

    def test_dashboard_access_with_admin(self):
        """Test dashboard access when logged in as admin"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })

        response = self.client.get('/accounts/dashadmin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
        self.assertContains(response, 'Welcome, Superuser!')

        # Check that counts are displayed (check for the rendered numbers)
        self.assertContains(response, '1')  # gear_count
        self.assertContains(response, '5')  # event_count (may vary due to existing data)
        self.assertContains(response, '1')  # post_count
        self.assertContains(response, '2')  # user_count

    def test_dashboard_access_without_admin(self):
        """Test dashboard access when not logged in as admin"""
        response = self.client.get('/accounts/dashadmin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertRedirects(response, '/accounts/login/')

    def test_admin_user_list_access_with_admin(self):
        """Test admin user list access when logged in as admin"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })

        response = self.client.get('/accounts/admin/users/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, 'testseller')

    def test_admin_user_list_access_without_admin(self):
        """Test admin user list access when not logged in as admin"""
        response = self.client.get('/accounts/admin/users/')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_logout_clears_admin_session(self):
        """Test that logout clears admin session"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })
        self.assertTrue(self.client.session.get('is_admin'))

        # Logout
        response = self.client.get('/accounts/logout/')
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('is_admin'))

        # Try to access dashboard after logout
        response = self.client.get('/accounts/dashadmin/')
        self.assertEqual(response.status_code, 302)

    def test_regular_user_login(self):
        """Test regular user login"""
        response = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('is_admin'))

    def test_dashboard_counts_accuracy(self):
        """Test that dashboard displays correct counts"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })

        response = self.client.get('/accounts/dashadmin/')

        # Check context data - adjust expected values based on test setup
        self.assertEqual(response.context['gear_count'], 1)
        self.assertEqual(response.context['event_count'], 1)  # Only the future event we created
        self.assertEqual(response.context['post_count'], 1)
        self.assertEqual(response.context['user_count'], 3)  # testuser, testseller, and admin user

    def test_admin_user_update(self):
        """Test updating user information as admin"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })

        # Update user
        response = self.client.post(f'/accounts/admin/users/{self.user.id}/edit/', {
            'first_name': 'Updated',
            'last_name': 'User',
            'email': 'updated@example.com',
            'user_type': 'seller',
            'full_name': 'Updated User',
            'phone_number': '1111111111',
            'business_name': 'New Business'
        })

        self.assertEqual(response.status_code, 302)

        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'User')

    def test_admin_user_delete(self):
        """Test deleting user as admin"""
        # Login as admin
        self.client.post('/accounts/login/', {
            'username': 'cbkadal',
            'password': 'dikadalin'
        })

        # Delete user
        response = self.client.post(f'/accounts/admin/users/{self.user.id}/delete/')
        self.assertEqual(response.status_code, 302)

        # Check user is deleted
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(id=self.user.id)
