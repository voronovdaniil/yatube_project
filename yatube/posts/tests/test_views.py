from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User, Group, Follow


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.AUTHOR = 'auth'
        cls.FOLLOWER = 'follower'
        cls.GROUP_TITLE = 'Тестовая группа'
        cls.GROUP_SLUG = 'test-slug'
        cls.OTHER_GROUP = 'Вторая группа'
        cls.OTHER_GROUP_SLUG = 'second-slug'
        cls.POST_TEXT = 'Тестовый текст'
        cls.OTHER_TEXT = 'Другой текст, для более точной проверки'

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
        cls.author_user = User.objects.create_user(username=cls.AUTHOR)
        cls.author = Client()
        cls.author.force_login(cls.author_user)
        cls.follower_user = User.objects.create_user(username=cls.FOLLOWER)
        cls.follower = Client()
        cls.follower.force_login(cls.follower_user)
        cls.group = Group.objects.create(
            title=cls.GROUP_TITLE,
            slug=cls.GROUP_SLUG
        )
        cls.other_group = Group.objects.create(
            title=cls.OTHER_GROUP,
            slug=cls.OTHER_GROUP_SLUG
        )
        cls.post = Post.objects.create(
            text=cls.POST_TEXT,
            author=cls.author_user,
            group=cls.group,
            image=cls.uploaded
        )
        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.author_user
        )
        cls.INDEX_URL = reverse('posts:index')
        cls.GROUP_LIST_URL = reverse('posts:group_list', kwargs={
                                     'slug': cls.GROUP_SLUG})
        cls.OTHER_GROUP_LIST_URL = reverse('posts:group_list',
                                           kwargs={'slug':
                                                   cls.OTHER_GROUP_SLUG})
        cls.PROFILE_URL = reverse('posts:profile', kwargs={
                                  'username': cls.AUTHOR})
        cls.FOLLOW_INDEX_URL = reverse('posts:follow_index')
        cls.POST_DETAIL_URL = reverse('posts:post_detail',
                                      kwargs={'post_id': cls.post.id})

    def test_post_pages_use_correct_context(self):
        """Контекст на страницах с группами и постами"""
        urls_posts = [
            [self.INDEX_URL, self.author],
            [self.GROUP_LIST_URL, self.author],
            [self.PROFILE_URL, self.author],
            [self.POST_DETAIL_URL, self.author],
            [self.FOLLOW_INDEX_URL, self.follower]
        ]
        for url, client in urls_posts:
            with self.subTest(url=url):
                response = client.get(url)
                if url == self.POST_DETAIL_URL:
                    post = response.context.get('post')
                else:
                    self.assertEqual((len(response.context['page_obj'])), 1)
                    post = response.context['page_obj'][0]
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.image, self.post.image)

    def test_author_on_profile_page(self):
        """Автор появляется на странице профиля"""
        response = self.author.get(self.PROFILE_URL)
        self.assertEqual(response.context.get('author'), self.author_user)

    def test_group_in_group_list(self):
        """Тест на отображение группы в списке групп"""
        response = self.author.get(self.GROUP_LIST_URL)
        group = response.context.get('group')
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.id, self.group.id)

    def test_post_not_in_other_group_or_subscription(self):
        """Пост не попал в чужую группу или подписку"""
        urls = [
            self.OTHER_GROUP_LIST_URL,
            self.FOLLOW_INDEX_URL
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertNotIn(self.post, response.context['page_obj'])
