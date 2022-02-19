import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Comment

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Author'),
        )
        Group.objects.create(
            title='Group',
            slug='slug',
            description='Description',
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
        post = get_object_or_404(Post, text='Тестовый текст')
        poster = post.author
        self.post_id = post.pk
        self.author = Client()
        self.author.force_login(poster)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый заголовок',
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Tester'})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый заголовок',
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует запись в Post."""
        form_data = {
            'text': 'Новый текст',
        }
        response = self.author.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post_id}),
            data=form_data,
            follow=True
        )

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id})
        )
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст',
            ).exists()
        )

    def test_create_post_for_guest(self):
        """Создание поста недоступно гостю"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый заголовок',
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(response, '/auth/login/?next=%2Fcreate%2F')
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый заголовок',
            ).exists()
        )

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
        self.assertEqual(Post.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id})
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Тестовый комментарий',
            ).exists()
        )
