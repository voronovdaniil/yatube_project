from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Group
from posts.config import POSTS_PER_PAGE




class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTHOR = 'auth'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.POST_TEXT = 'Тестовый текст'
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG)
        cls.posts_amount = POSTS_PER_PAGE + 3
        bulk_posts = [
            Post(
                text=cls.POST_TEXT,
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
        first_page = POSTS_PER_PAGE
        second_page = 3
        paginator_data = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list',
                kwargs={'slug': self.GROUP_SLUG}
            ),
            'profile': reverse(
                'posts:profile',
                kwargs={'username': self.AUTHOR}
            )
        }
        for paginator_place, paginator_page in paginator_data.items():
            with self.subTest(paginator_place=paginator_place):
                response_page_1 = self.client.get(paginator_page)
                response_page_2 = self.client.get(
                    paginator_page + '?page=2'
                )
                self.assertEqual(len(
                    response_page_1.context['page_obj']),
                    first_page
                )
                self.assertEqual(len(
                    response_page_2.context['page_obj']),
                    second_page
                )
