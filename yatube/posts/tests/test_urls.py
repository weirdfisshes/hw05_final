from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.core.cache import cache

from ..models import Post, Group, User

User = get_user_model()


class PostURLTests(TestCase):
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

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
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
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post_id}
            ): 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)

    def test_public_urls_exist_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю"""
        ANSWER = 200
        url_names = {
            reverse('posts:index'): ANSWER,
            reverse('posts:group_list', kwargs={'slug': 'slug'}): ANSWER,
            reverse('posts:profile', kwargs={'username': 'Tester'}): ANSWER,
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post_id}
            ): ANSWER,
            reverse('about:author'): ANSWER,
            reverse('about:tech'): ANSWER,
        }
        for url, answer in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, answer)

    def test_unexist_page(self):
        """Несуществующая страница недоступна"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_exists_for_author(self):
        """/edit/ доступна автору поста"""
        response = self.author.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id})
        )
        self.assertEqual(response.status_code, 200)

    def test_create_exists_at_desired_location(self):
        """/create/ доступна авторизованному пользователю"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, 200)

    def test_create_url_redirect_anonymous_on_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get(reverse(
            'posts:post_create'
        ), follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_edit_url_redirect_not_author_on_detail(self):
        """Страница /edit/ перенаправит не автора на страницу /post/pk/"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post_id}
        ), follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_id})
        )

    def test_comments_for_authorised(self):
        """Комментарии недоступны неавторизированному."""
        response = self.guest_client.get(reverse(
            'posts:add_comment', kwargs={'post_id': self.post_id})
        )
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/comment/')
