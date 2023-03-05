from django.test import TestCase
from django.urls import reverse

from posts.urls import app_name

USERNAME = 'username'
GROUP_SLUG = 'slug'
POST_ID = 1


class RoutesModelTest(TestCase):

    def test_routes(self):
        """Проверяем маршруты"""
        routes = [
            ['/', 'index', None],
            [f'/group/{GROUP_SLUG}/', 'group_list', [GROUP_SLUG]],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
            ['/create/', 'post_create', None],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/posts/{POST_ID}/comment', 'add_comment', [POST_ID]],
            ['/follow/', 'follow_index', None],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]]
        ]
        for url, name, arg in routes:
            self.assertEqual(url, reverse(f'{app_name}:{name}', args=arg))
