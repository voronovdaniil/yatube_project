from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, User


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTHOR = 'auth'
        cls.POST_TEXT = 'Тестовый текст'
        cls.INDEX_URL = reverse('posts:index')
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.post = Post.objects.create(
            text=cls.POST_TEXT,
            author=cls.author,
        )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_index_cache(self):
        content_one = self.author_client.get(self.INDEX_URL).content
        self.post.delete()
        content_two = self.author_client.get(self.INDEX_URL).content
        self.assertEqual(content_one, content_two)
        cache.clear()
        content_three = self.author_client.get(self.INDEX_URL).content
        self.assertNotEqual(content_one, content_three)
