from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Follow


class FormsTests(TestCase):
    """Тестирует механизмы подписки на автора и отписки от него"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTER = 'poster'
        cls.NEW_FOLLOWER = 'new_follower'
        cls.NOT_FOLLOWER = 'not_follower'
        cls.POST_TEXT = 'Тестовый текст'
        cls.unfollower = User.objects.create_user(username=cls.NOT_FOLLOWER)
        cls.poster = User.objects.create_user(username=cls.POSTER)
        cls.new_follower = User.objects.create_user(username=cls.NEW_FOLLOWER)
        cls.post = Post.objects.create(
            text=cls.POST_TEXT,
            author=cls.poster
        )
        cls.unfollower_client = Client()
        cls.unfollower_client.force_login(cls.unfollower)
        cls.new_follower_client = Client()
        cls.new_follower_client.force_login(cls.new_follower)

        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')
        cls.FOLLOW_URL = reverse('posts:profile_follow',
                                 kwargs={'username': cls.POSTER})
        cls.UNFOLLOW_URL = reverse('posts:profile_unfollow',
                                   kwargs={'username': cls.POSTER})

    def test_subscribe(self):
        """Тестирование подписки"""
        follows_before = Follow.objects.count()
        self.new_follower_client.get(self.FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follows_before + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.new_follower,
                author=self.poster
            ).exists()
        )

    def test_unsubscribe(self):
        """Тестирование отписки"""
        Follow.objects.create(
            user=self.unfollower,
            author=self.poster
        )
        follows_before = Follow.objects.count()
        self.unfollower_client.get(self.UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follows_before - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.unfollower,
                author=self.poster
            ).exists()
        )
