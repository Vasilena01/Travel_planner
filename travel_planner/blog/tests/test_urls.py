from django.test import SimpleTestCase
from django.urls import resolve, reverse
from blog.views import list_posts, get_post_detail, create_post, delete_post, edit_post

class TestBlogUrls(SimpleTestCase):
    def test_list_posts_url_resolves(self):
        url = reverse('list_posts')
        self.assertEqual(resolve(url).func, list_posts)

    def test_get_post_detail_url_resolves(self):
        url = reverse('post_detail', args=[1])
        self.assertEqual(resolve(url).func, get_post_detail)

    def test_create_post_url_resolves(self):
        url = reverse('create_post')
        self.assertEqual(resolve(url).func, create_post)

    def test_delete_post_url_resolves(self):
        url = reverse('delete_post', args=[1])
        self.assertEqual(resolve(url).func, delete_post)

    def test_edit_post_url_resolves(self):
        url = reverse('edit_post', args=[1])
        self.assertEqual(resolve(url).func, edit_post)