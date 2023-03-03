from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus
from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст поста',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Страницы доступны любому и авторизованным пользователям."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug':
                            PostURLTests.group.slug}),
            reverse('posts:profile',
                    kwargs={'username':
                            PostURLTests.user.username}),
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            PostURLTests.post.id}),
        ]
        for request_client in (self.guest_client, self.authorized_client):
            for url in urls:
                with self.subTest(url=url, request_client=request_client):
                    response = request_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
        urls = [
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostURLTests.post.id}),
            reverse('posts:post_create'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_anonymous(self):
        """Страница /post_id/edit перенаправляет анонимного пользователя."""
        response = self.guest_client.get(reverse('posts:post_edit',
                                                 kwargs={'post_id':
                                                         PostURLTests.
                                                         post.id}))
        self.assertRedirects(response, '/auth/login/?next=/posts/1/edit/')

    def test_post_create_url_redirect_anonymous(self):
        """Страница /posts/create/ перенаправляет анонимного пользователя. """
        response = self.guest_client.get(reverse('posts:post_create'),
                                         follow=True)
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_unexisting_page(self):
        """Запрос к страница unixisting_page вернет ошибку 404"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts',
                    kwargs={'slug':
                            PostURLTests.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username':
                            PostURLTests.user.username}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id':
                            PostURLTests.post.id}): 'posts/post_detail.html',
            reverse('posts:post_edit',
                    kwargs={'post_id':
                            PostURLTests.post.id}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
