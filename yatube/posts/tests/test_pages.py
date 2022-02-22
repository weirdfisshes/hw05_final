from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ..models import Post, Group, User

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        author = User.objects.create_user(username='Author')
        for posts in range(12):
            Post.objects.create(
                text='Пост без группы',
                author=author
            )
        Post.objects.create(
            text='Пост с группой',
            author=author,
            group=Group.objects.create(
                title='Group',
                slug='slug',
                description='Description'
            )
        )

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

    def test_paginator_works(self):
        response = (self.authorized_client.get(reverse('posts:index')))
        response_2 = (self.authorized_client.get(reverse(
            'posts:index'), {'page': 2})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_2.context['page_obj']), 3)
        response = (self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'slug'}))
        )
        self.assertEqual(len(response.context['page_obj']), 1)
        response = (self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'Author'}))
        )
        response_2 = (self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': 'Author'}), {'page': 2})
        )
        self.assertEqual(len(response.context['page_obj']), 10)
        self.assertEqual(len(response_2.context['page_obj']), 3)
