from django.contrib.auth import get_user_model
from django.test import TestCase
from django.core.cache import cache

from ..models import Group, Post
from yatube.settings import FIRST_POST_SYMBOLS

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cache.clear()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_str_len_is_15_symbols(self):
        '''Проверка длины post.__str__()'''
        post = PostModelTest.post
        length_post = len(post.__str__())
        self.assertGreaterEqual(FIRST_POST_SYMBOLS, length_post)

    def test_post_str_is_first_15_symbols(self):
        '''Проверяем, что post.__str__() возвращает первые N символов'''
        post = PostModelTest.post
        str_post = post.text[:FIRST_POST_SYMBOLS]
        self.assertGreaterEqual(str_post, post.__str__())

    def test_group_name(self):
        '''Проверяем, что group.__str__() возвращает название группы'''
        group = PostModelTest.group
        str_group = group.title
        self.assertGreaterEqual(str_group, group.__str__())
