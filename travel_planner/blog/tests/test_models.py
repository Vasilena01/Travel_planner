from django.test import TestCase
from django.contrib.auth.models import User
from blog.models import Post
from django.utils import timezone

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.post = Post.objects.create(
            title='Test Post',
            content='This is a test content.',
            author=self.user
        )

    def test_post_creation(self):
        """Test that a Post object is created correctly."""
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.content, 'This is a test content.')
        self.assertEqual(self.post.author, self.user)
        self.assertTrue(isinstance(self.post.date_posted, timezone.datetime))

    def test_post_str_representation(self):
        """Test the string representation of the Post model."""
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_default_date_posted(self):
        """Test that the default date_posted is set to now."""
        self.assertAlmostEqual(self.post.date_posted, timezone.now(), delta=timezone.timedelta(seconds=1))