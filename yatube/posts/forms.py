from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Группа поста'
        }
        help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу поста (необязательно)'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария',
        }
        help_texts = {
            'text': 'Введите текст комментария',
        }
