import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Comment
from posts.forms import PostForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(username='test-user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description',
        )
        self.post = Post.objects.create(
            text='Тестовый текст lkz htlfrwbb',
            author=self.user,
            group=self.group,
        )

    def test_create_post(self):
        '''Проверка создания поста'''
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        image_name = 'posts/test.gif'
        uploaded = SimpleUploadedFile(
            name=image_name,
            content=small_gif,
            content_type='image/jpg'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=form_data['text'],
                image=image_name,
            ).exists()
        )

    def test_edit_post(self):
        '''Тестирование Редактирования'''
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост'
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                id=self.post.id,
                text=form_data['text'],
            ).exists()
        )

    def test_comment(self):
        '''Проверка комментирования'''
        form_data = {
            'text': 'Тестовый comment'
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
                post=self.post,
                author=self.user
            ).exists()
        )
