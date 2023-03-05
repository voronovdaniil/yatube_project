from django.test import TestCase

from posts.models import Group, Post, User

AUTHOR = 'auth'
GROUP_TITLE = 'Тестовая группа'
GROUP_SLUG = 'test-slug'
POST_TEXT = 'Для проверки укорачивания длины здесь больше 15 символов'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title=GROUP_TITLE,
            slug=GROUP_SLUG,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        self.assertEqual(self.post.text[:15], str(self.post))
        self.assertEqual(self.group.title, str(self.group))
