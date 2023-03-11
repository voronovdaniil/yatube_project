import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Post, User, Group, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.AUTHOR = 'auth'
        cls.ANOTHER = 'another'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.NEW_GROUP_TITLE = 'Новая группа'
        cls.NEW_GROUP_SLUG = 'new-slug'
        cls.POST_TEXT = 'Тестовый текст'
        cls.NEW_TEXT = 'Новый текст'
        cls.NEW_COMMENT = 'Новый комментарий'
        cls.author = User.objects.create_user(username=cls.AUTHOR)
        cls.another = User.objects.create_user(username=cls.ANOTHER)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG,
        )
        cls.new_group = Group.objects.create(
            title=cls.NEW_GROUP_TITLE,
            slug=cls.NEW_GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            text=cls.POST_TEXT,
            author=cls.author,
            group=cls.group,
            image=cls.uploaded
        )
        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.another_client = Client()
        cls.another_client.force_login(cls.another)
        cls.PROFILE_URL = reverse('posts:profile', kwargs={
                                  'username': cls.AUTHOR})
        cls.POST_CREATE_URL = reverse('posts:post_create')
        cls.LOGIN_URL = reverse('users:login')
        cls.POST_EDIT_URL = reverse('posts:post_edit',
                                    kwargs={'post_id': cls.post.id})
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})
        cls.ADD_COMMENT_URL = reverse('posts:add_comment',
                                      kwargs={'post_id': cls.post.id})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_form_create(self):
        """Проверка создания нового поста"""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        posts = set(Post.objects.all())
        post_count = Post.objects.count()
        form_data = {
            'text': self.NEW_TEXT,
            'group': self.group.id,
            'image': uploaded
        }
        response = self.author_client.post(self.POST_CREATE_URL,
                                           data=form_data,
                                           follow=True)
        self.assertRedirects(response, self.PROFILE_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        posts = set(Post.objects.all()) - posts
        self.assertEqual(len(posts), 1)
        post = posts.pop()
        self.assertEqual(self.author, post.author)
        self.assertEqual(form_data['text'], post.text)
        self.assertEqual(form_data['group'], post.group.id)
        self.assertEqual(form_data['image'], uploaded)

    def test_add_comment_auth_user(self):
        """Проверка создания нового коммента авторизованным"""
        comments = set(Comment.objects.all())
        comment_count = Comment.objects.count()
        form_data = {
            'text': self.NEW_COMMENT,
        }
        response = self.author_client.post(self.ADD_COMMENT_URL,
                                           data=form_data,
                                           follow=True)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        comments = set(Comment.objects.all()) - comments
        self.assertEqual(len(comments), 1)
        comment = (comments).pop()
        self.assertEqual(form_data['text'], comment.text)
        self.assertEqual(self.author, comment.author)
        self.assertEqual(self.post, comment.post)

    def test_add_comment_guest_user(self):
        """Проверка создания нового коммента гостем"""
        comments_before = set(Comment.objects.all())
        self.guest_client.post(self.ADD_COMMENT_URL, {'text': self.NEW_TEXT})
        comments_after = set(Comment.objects.all())
        self.assertEqual(comments_before, comments_after)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_post_edit(self):
        """Проверка редактирования поста"""
        uploaded_new = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': self.NEW_TEXT,
            'group': self.new_group.id,
            'image': uploaded_new
        }
        past_author = self.post.author
        response = self.author_client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.post.refresh_from_db()
        self.assertEqual(form_data['text'], self.post.text)
        self.assertEqual(form_data['image'], uploaded_new)
        self.assertEqual(form_data['group'], self.post.group.id)
        self.assertEqual(self.post.author, past_author)

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_post_deny_edit(self):
        """Проверка редактирования поста гостем или неавтором"""
        uploaded_new = SimpleUploadedFile(
            name='small2.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': self.NEW_TEXT,
            'group': self.new_group.id,
            'image': uploaded_new
        }
        clients_redirects = {
            self.guest_client: f'{self.LOGIN_URL}?next={self.POST_EDIT_URL}',
            self.another_client: self.POST_DETAIL_URL
        }
        for client, url in clients_redirects.items():
            past_author = self.post.author
            response = client.post(
                self.POST_EDIT_URL,
                data=form_data,
                follow=True
            )
        self.assertRedirects(response, url)
        self.post.refresh_from_db()
        self.assertEqual(self.POST_TEXT, self.post.text)
        self.assertEqual(self.group.id, self.post.group.id)
        self.assertEqual(self.post.author, past_author)
        self.assertEqual(self.post.image, self.post.image)

    def test_post_create_edit_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        urls = (
            self.POST_EDIT_URL,
            self.POST_CREATE_URL
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                for value, expected in form_fields.items():
                    with self.subTest(url=url):
                        form_field = response.context['form'].fields[value]
                        self.assertIsInstance(form_field, expected)
