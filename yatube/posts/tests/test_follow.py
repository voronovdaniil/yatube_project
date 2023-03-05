from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Follow

POSTER = 'poster'
NEW_FOLLOWER = 'new_follower'
NOT_FOLLOWER = 'not_follower'
POST_TEXT = 'Тестовый текст'
POST_CREATE_URL = reverse('posts:post_create')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow',
                     kwargs={'username': POSTER})
UNFOLLOW_URL = reverse('posts:profile_unfollow',
                       kwargs={'username': POSTER})


class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.unfollower = User.objects.create_user(username=NOT_FOLLOWER)
        cls.poster = User.objects.create_user(username=POSTER)
        cls.new_follower = User.objects.create_user(username=NEW_FOLLOWER)
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.poster
        )
        cls.unfollower_client = Client()
        cls.unfollower_client.force_login(cls.unfollower)
        cls.new_follower_client = Client()
        cls.new_follower_client.force_login(cls.new_follower)

    def test_subscribe(self):
        follows_before = Follow.objects.count()
        self.new_follower_client.get(FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follows_before + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.new_follower,
                author=self.poster
            ).exists()
        )

    def test_unsubscribe(self):
        Follow.objects.create(
            user=self.unfollower,
            author=self.poster
        )
        follows_before = Follow.objects.count()
        self.unfollower_client.get(UNFOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follows_before - 1)
        self.assertFalse(
            Follow.objects.filter(
                user=self.unfollower,
                author=self.poster
            ).exists()
        )
