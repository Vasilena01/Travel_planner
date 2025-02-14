from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from blog.models import Post

class BlogViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="password123")
        
        # Dummy image file
        self.image = SimpleUploadedFile("test_image.jpg", b"file_content", content_type="image/jpeg")

        self.post = Post.objects.create(
            title="Test trip",
            content="This is a test trip post.",
            author=self.user,
            image=self.image
        )

    def test_list_posts_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse('list_posts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test trip")

    def test_list_posts_unauthenticated(self):
        response = self.client.get(reverse('list_posts'))
        self.assertEqual(response.status_code, 302)

    def test_get_post_detail_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.get(reverse('post_detail', args=[self.post.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This is a test trip post.")

    def test_create_post_authenticated(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse('create_post'), {
            'title': 'New post',
            'content': 'This is a new post.',
        }, files={'image': self.image})
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(title="New post").exists())

    def test_create_post_unauthenticated(self):
        response = self.client.post(reverse('create_post'), {
            'title': 'Unauthorized Post',
            'content': 'Should not be allowed.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(title="Unauthorized Post").exists())

    def test_edit_post_authorized(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse('edit_post', args=[self.post.id]), {
            'title': 'Edited Post',
            'content': 'Edited content.',
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, "Edited Post")

    def test_edit_post_unauthorized(self):
        another_user = User.objects.create_user(username="anotheruser", password="password123")
        self.client.login(username="anotheruser", password="password123")
        response = self.client.post(reverse('edit_post', args=[self.post.id]), {
            'title': 'Not allowed to edit Post',
            'content': 'Not allowed to edit content.',
        })
        self.assertEqual(response.status_code, 302)
        self.post.refresh_from_db()
        self.assertNotEqual(self.post.title, "Not allowed to edit Post")

    def test_delete_post_authorized(self):
        self.client.login(username="testuser", password="password123")
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Post.objects.filter(id=self.post.id).exists())

    def test_delete_post_unauthorized(self):
        another_user = User.objects.create_user(username="anotheruser", password="password123")
        self.client.login(username="anotheruser", password="password123")
        response = self.client.post(reverse('delete_post', args=[self.post.id]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Post.objects.filter(id=self.post.id).exists())