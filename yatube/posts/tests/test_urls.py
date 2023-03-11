from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Group, Post, User


class PostGroupProfileURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTHORIZED = 'another'
        cls.AUTHOR = 'auth'
        cls.POSTER = 'poster'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.POST_TEXT = 'Тестовый текст'
        cls.another_user = User.objects.create_user(username=cls.AUTHORIZED)
        cls.author_user = User.objects.create_user(username=cls.AUTHOR)
        cls.poster_user = User.objects.create_user(username=cls.POSTER)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text=cls.POST_TEXT,
            author=cls.author_user,
        )
        cls.guest = Client()
        cls.another = Client()
        cls.another.force_login(cls.another_user)
        cls.author = Client()
        cls.author.force_login(cls.author_user)

        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_LIST_URL = reverse('posts:group_list', kwargs={
                                     'slug': cls.GROUP_SLUG})
        cls.PROFILE_URL = reverse('posts:profile', kwargs={
                                  'username': cls.AUTHOR})
        cls.PROFILE_POSTER_URL = reverse(
            'posts:profile', kwargs={'username': cls.POSTER})
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.LOGIN_URL = reverse('users:login')
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')
        cls.FOLLOW_URL = reverse('posts:profile_follow',
                                 kwargs={'username': cls.POSTER})
        cls.UNFOLLOW_URL = reverse('posts:profile_unfollow',
                                   kwargs={'username': cls.POSTER})
        cls.FOLLOW_SELF_URL = reverse('posts:profile_follow',
                                      kwargs={'username': cls.AUTHOR})
        cls.UNFOLLOW_SELF_URL = reverse('posts:profile_unfollow',
                                        kwargs={'username': cls.AUTHOR})
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})

    def test_url_responses(self):
        """Тестируем доступность страниц"""
        data_list = [
            [self.INDEX_URL, self.guest, HTTPStatus.OK.value],
            [self.GROUP_LIST_URL, self.guest, HTTPStatus.OK.value],
            [self.PROFILE_URL, self.guest, HTTPStatus.OK.value],
            [self.POST_DETAIL_URL, self.guest, HTTPStatus.OK.value],
            [self.POST_CREATE_URL, self.guest, HTTPStatus.FOUND.value],
            [self.POST_EDIT_URL, self.guest, HTTPStatus.FOUND.value],
            [self.FOLLOW_INDEX_URL, self.guest, HTTPStatus.FOUND.value],
            [self.POST_CREATE_URL, self.another, HTTPStatus.FOUND.value],
            [self.POST_EDIT_URL, self.another, HTTPStatus.FOUND.value],
            [self.FOLLOW_INDEX_URL, self.another, HTTPStatus.FOUND.value],
            [self.POST_EDIT_URL, self.author, HTTPStatus.FOUND.value],
            [self.FOLLOW_URL, self.guest, HTTPStatus.FOUND.value],
            [self.UNFOLLOW_URL, self.guest, HTTPStatus.FOUND.value],
            [self.FOLLOW_URL, self.author, HTTPStatus.FOUND.value],
            [self.UNFOLLOW_URL, self.author, HTTPStatus.FOUND.value],
            [self.FOLLOW_SELF_URL, self.author, HTTPStatus.FOUND.value],
            [self.UNFOLLOW_SELF_URL, self.author, HTTPStatus.FOUND.value]
        ]
        for url, client, status in data_list:
            response = self.client.get(url)
            print(response.status_code)
        for url, client, status in data_list:
            with self.subTest(url=url, client=client, status=status):
                self.assertEqual(self.client.get(
                    url).status_code, status)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            self.GROUP_LIST_URL: 'posts/group_list.html',
            self.PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            self.POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html',
            self.FOLLOW_INDEX_URL: 'posts/follow.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(self.author.get(adress),
                                        template)

    def test_urls_redirect_correctly(self):
        """URL-адреса перенаправляются на нужные."""
        urls_users = [
            [self.POST_CREATE_URL,
             f'{self.LOGIN_URL}?next={self.POST_CREATE_URL}',
             self.guest],
            [self.POST_EDIT_URL, f'{self.LOGIN_URL}?next={self.POST_EDIT_URL}',
             self.guest],
            [self.FOLLOW_INDEX_URL,
             f'{self.LOGIN_URL}?next={self.FOLLOW_INDEX_URL}',
             self.guest],
            [self.POST_EDIT_URL, self.POST_DETAIL_URL, self.another],
            [self.FOLLOW_URL,
                f'{self.LOGIN_URL}?next={self.FOLLOW_URL}', self.guest],
            [self.UNFOLLOW_URL,
                f'{self.LOGIN_URL}?next={self.UNFOLLOW_URL}', self.guest],
            [self.FOLLOW_URL, self.PROFILE_POSTER_URL, self.author],
            [self.UNFOLLOW_URL, self.PROFILE_POSTER_URL, self.author],
            [self.FOLLOW_SELF_URL, self.PROFILE_URL, self.author],
        ]
        for url, redirect, user in urls_users:
            with self.subTest(url=url, user=user):
                self.assertRedirects(user.get(url, follow=True), redirect)
