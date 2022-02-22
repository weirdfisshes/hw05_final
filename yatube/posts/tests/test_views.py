import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import SimpleUploadedFile
from django import forms
from django.conf import settings
from django.core.cache import cache

from ..models import Post, Group, User, Comment
from ..forms import PostForm

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Author')
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        Post.objects.create(
            text='Пост с другой группой',
            author=author,
            group=Group.objects.create(
                title='Вторая группа',
                slug='empty',
                description='Еще одна группа'
            ),
        )
        Post.objects.create(
            text='Пост с группой',
            author=author,
            group=Group.objects.create(
                title='Group',
                slug='slug',
                description='Description'
            ),
            image=SimpleUploadedFile(
                name='small.gif',
                content=small_gif,
                content_type='image/gif'
            ),
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Tester')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        post = get_object_or_404(Post, text='Пост с группой')
        poster = post.author
        self.post_id = post.pk
        self.author = Client()
        self.author.force_login(poster)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': 'slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': 'Tester'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post_id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author.username
        post_pub_date_0 = first_object.pub_date
        post_group_0 = first_object.group.title
        post_image_0 = first_object.image
        self.assertEqual(post_text_0, 'Пост с группой')
        self.assertEqual(post_author_0, 'Author')
        self.assertIsNotNone(post_pub_date_0)
        self.assertEqual(post_group_0, 'Group')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug'})
        )
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group.title
        post_text_0 = first_object.text
        post_image_0 = first_object.image
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertEqual(post_group_0, 'Group')
        self.assertEqual(post_text_0, 'Пост с группой')
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'empty'})
        )
        object = response.context['page_obj'][0]
        post_group_0 = object.group.title
        post_text_0 = object.text
        self.assertNotEqual(post_group_0, 'Group')
        self.assertNotEqual(post_text_0, 'Пост с группой')

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'Author'})
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author.username
        post_image_0 = first_object.image
        self.assertEqual(post_author_0, 'Author')
        self.assertEqual(post_image_0, 'posts/small.gif')

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id})
        )
        object = response.context['post_detail']
        number = response.context['number']
        post_id_0 = object.pk
        post_image_0 = object.image
        self.assertEqual(post_image_0, 'posts/small.gif')
        self.assertEqual(post_id_0, self.post_id)
        self.assertEqual(number, 2)

    def test_create_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_show_correct_context(self):
        """edit формируется с верным контекстом"""
        response = self.author.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id})
        )
        form_fields = {
            'text': 'Пост с группой',
            'group': 2,
        }
        is_edit = response.context['is_edit']
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        self.assertTrue(is_edit)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').initial.get(value)
                self.assertEqual(form_field, expected)

    def test_index_cache(self):
        """Кэш работает."""
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        before = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        after = response.content
        self.assertEqual(before, after)

    def test_follow_works(self):
        """Подписка работает."""
        cache.clear()
        author = get_object_or_404(User, username='Author')
        response = self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'})
        )
        posts = Post.objects.filter(author__following__user=self.user).exists()
        self.assertTrue(posts)
        Post.objects.create(
            text='Проверка подписок',
            author=author,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        post = response.context['page_obj'][0].text
        self.assertEqual(post, 'Проверка подписок')

    def test_follow_index_for_not_follower(self):
        cache.clear()
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'})
        )
        stranger = User.objects.create_user(username='Stranger')
        strange_client = Client()
        strange_client.force_login(stranger)
        author = get_object_or_404(User, username='Author')
        Post.objects.create(
            text='Проверка подписок',
            author=author,
        )
        response_1 = strange_client.get(reverse('posts:follow_index'))
        response_2 = self.authorized_client.get(reverse('posts:follow_index'))
        first = response_1.content
        second = response_2.content
        self.assertNotEqual(first, second)

    def test_unfollow(self):
        self.authorized_client.get(reverse(
            'posts:profile_follow', kwargs={'username': 'Author'})
        )
        self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'Author'})
        )
        posts = Post.objects.filter(author__following__user=self.user).exists()
        self.assertFalse(posts)

    def test_leave_a_comment(self):
        """Валидная форма добавляет комментарий"""
        post = get_object_or_404(Post, pk=self.post_id)
        comment_count = post.comments.all().count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(post.comments.all().count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id})
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
            ).exists()
        )
