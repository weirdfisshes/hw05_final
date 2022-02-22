from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
NUM_OF_SYM = 15


class Group(models.Model):
    title = models.CharField(
        'Название',
        max_length=200,
        help_text='Название группы'
    )
    slug = models.SlugField(
        'Адрес',
        unique=True,
        help_text='Адрес группы',
    )
    description = models.TextField(
        'Описание',
        help_text='Описание группы'
    )

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст',
        help_text='Текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата',
        auto_now_add=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Выберите группу',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:NUM_OF_SYM]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        'Текст',
        help_text='Текст комментария',
    )
    created = models.DateTimeField(
        'Дата',
        auto_now_add=True,
    )

    def __str__(self):
        return self.text[:NUM_OF_SYM]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        null=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        null=True,
    )

    def __str__(self):
        return self.author.username
