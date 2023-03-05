from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Group
from posts.settings import POSTS_PER_PAGE

AUTHOR = 'auth'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
POST_TEXT = 'Тестовый текст'
INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', kwargs={'slug': GROUP_SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': AUTHOR})


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG)
        cls.posts_amount = POSTS_PER_PAGE + 3
        bulk_posts = [
            Post(
                text=POST_TEXT,
                author=cls.author,
                group=cls.group,
            )
            for i in range(cls.posts_amount)
        ]
        Post.objects.bulk_create(bulk_posts)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_paginator(self):
        urls = {
            INDEX_URL: POSTS_PER_PAGE,
            INDEX_URL + '?page=2': 3,
            GROUP_LIST_URL: POSTS_PER_PAGE,
            GROUP_LIST_URL + '?page=2': 3,
            PROFILE_URL: POSTS_PER_PAGE,
            PROFILE_URL + '?page=2': 3
        }
        for url, number in urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(len(response.context['page_obj']), number)
