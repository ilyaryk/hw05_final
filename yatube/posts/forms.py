from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу'}
        help_texts = {'text': 'Текст вашего поста', 'group': 'Список групп'}
        widgets = {
            'group': forms.Select()
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Введите текст', }
        help_texts = {'text': 'Текст вашего поста', }
