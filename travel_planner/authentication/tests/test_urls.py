from django.test import SimpleTestCase
from django.urls import reverse, resolve
from authentication import views

class AuthenticationUrlsTest(SimpleTestCase):

    def test_register_url(self):
        url = reverse('register')
        self.assertEqual(resolve(url).func, views.register_user)

    def test_login_url(self):
        url = reverse('login')
        self.assertEqual(resolve(url).func, views.login_user)

    def test_logout_url(self):
        url = reverse('logout')
        self.assertEqual(resolve(url).func, views.logout_user)