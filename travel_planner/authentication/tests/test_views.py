from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages

class AuthenticationViewsTest(TestCase):

    def test_register_user_success(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('login'))
        messages = list(response.wsgi_request._messages)
        self.assertEqual(str(messages[0]), 'Account created successfully. Please login.')
        
    def test_register_user_invalid_email(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'password123',
            'confirm_password': 'password123',
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address.")

    def test_register_user_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123',
            'confirm_password': 'password321',
        }
        response = self.client.post(url, data)
        self.assertContains(response, 'Passwords do not match.')

    def test_register_user_username_taken(self):
        User.objects.create_user(username='testuser', email='existing@example.com', password='password123')
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertContains(response, 'A user with that username already exists.')

    def test_login_user_success(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'password123',
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('homepage'))

    def test_login_user_invalid_credentials(self):
        url = reverse('login')
        data = {
            'username': 'wronguser',
            'password': 'wrongpassword',
        }
        response = self.client.post(url, data)
        self.assertContains(response, 'Invalid username or password')

    def test_logout_user(self):
        user = User.objects.create_user(username='testuser', email='testuser@example.com', password='password123')
        self.client.login(username='testuser', password='password123')
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('homepage'))