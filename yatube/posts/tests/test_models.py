from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='follow')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки вывода 15 символов',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария. Текст комментария.',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author,
        )

    def test_group_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_posts_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_comment_have_correct_object_names(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = PostModelTest.comment
        expected_object_name = comment.text[:15]
        self.assertEqual(expected_object_name, str(comment))

    def test_follow_have_correct_object_names(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = PostModelTest.follow
        expected_object_name = follow.author.username
        self.assertEqual(expected_object_name, str(follow))

    def test_group_verbose_name(self):
        """Group verbose_name в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_post_verbose_name(self):
        """Post verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        """Group help_text в полях совпадает с ожидаемым."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Адрес группы',
            'description': 'Описание группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)

    def test_post_help_text(self):
        """Post help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_comment_verbose_name(self):
        """Comment verbose_name в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        field_verboses = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст',
            'created': 'Дата',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_follow_verbose_name(self):
        """Follow verbose_name в полях совпадает с ожидаемым."""
        follow = PostModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_comment_help_text(self):
        """Comment help_text в полях совпадает с ожидаемым."""
        comment = PostModelTest.comment
        self.assertEqual(
            comment._meta.get_field('text').help_text, 'Текст комментария'
        )
