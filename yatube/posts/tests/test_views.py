import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Post, Group, Follow
from yatube.settings import POSTS_SHOW
from posts.forms import PostForm


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostsPagesTests(TestCase):
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
            description='test-description'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='posts/test.gif',
            content=small_gif,
            content_type='image/jpg'
        )
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group,
                                        image=uploaded
                                        )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': self.user}),
            'posts/posts.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
            'posts/create_post.html': (
                reverse('posts:post_create'))
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_url(self):
        '''URL-адрес post_edit использует соответствующий шаблон.'''
        reverse_name = reverse('posts:post_edit',
                               kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(reverse_name)
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_group_list_show_correct_context(self):
        '''group_list имеет правильный контекст'''
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug':
                            self.group.slug}))
        response_group = response.context['page_obj'][0].group.title
        response_id = response.context['page_obj'][0].group.id
        response_image = response.context['page_obj'][0].image
        self.assertEqual(response_image, self.post.image)
        self.assertEqual(response_group, self.group.title)
        self.assertEqual(response_id, self.group.id)

    def test_profile_show_correct_context(self):
        '''profile имеет правильный контекст'''
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author}))
        response_author = response.context['page_obj'][0].author.username
        response_author_id = response.context['page_obj'][0].author.id
        response_image = response.context['page_obj'][0].image
        self.assertEqual(response_image, self.post.image)
        self.assertEqual(response_author, 'test-user')
        self.assertEqual(response_author_id, self.user.id)

    def test_index_show_correct_context(self):
        '''index имеет правильный контекст'''
        response = self.authorized_client.get(reverse('posts:index'))
        response_group = response.context['page_obj'][0].group
        self.assertEqual(response_group, self.post.group)
        response_id = response.context['page_obj'][0].id
        self.assertEqual(response_id, self.post.id)
        response_image = response.context['page_obj'][0].image
        self.assertEqual(response_image, self.post.image)

    def test_post_detail_correct_context(self):
        '''post_detail имеет правильный контекст'''
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': self.post.id}))
        response_post = response.context['post']
        self.assertEqual(response_post, self.post)

    def test_create_post_correct_context(self):
        '''create_post имеет правильный контекст'''
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_correct_context(self):
        '''edit_post имеет правильный контекст'''
        response = self.authorized_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_show_recent_posts(self):
        '''Недавние посты показываются на странице profile'''
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author}))
        response_text = response.context['page_obj'][0].text
        self.assertEqual(response_text, self.post.text)

    def test_index_show_recent_posts(self):
        '''Недавние посты показываются на странице index'''
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author}))
        response_text = response.context['page_obj'][0].text
        self.assertEqual(self.post.text, response_text)

    def test_group_list_show_recent_posts(self):
        '''Недавние посты показываются на странице group_list'''
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': 'test-slug'}))
        response_ = response.context['page_obj']
        self.assertIn(self.post, response_)

    def test_paginators_show_correct_context(self):
        '''Тестирование paginator-ов'''
        for i in range(0, 13):
            self.post = Post.objects.create(
                text=f'Тестовый текст {i}',
                author=self.user,
                group=self.group,
            )
        response = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug':
                            self.group.slug}))
        response_len = len(response.context['page_obj'])
        self.assertEqual(response_len, POSTS_SHOW)
        response = self.authorized_client.get(reverse('posts:index'))
        response_len = len(response.context['page_obj'])
        self.assertEqual(response_len, POSTS_SHOW)
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username':
                            self.post.author}))
        response_len = len(response.context['page_obj'])
        self.assertEqual(response_len, POSTS_SHOW)

    def test_check_cache(self):
        """Проверка кеша."""
        response = self.client.get(reverse("posts:index"))
        response_1 = response.content
        Post.objects.get(id=self.post.id).delete()
        response2 = self.client.get(reverse("posts:index"))
        response_2 = response2.content
        self.assertEqual(response_1, response_2)
        cache.clear()
        response_after_cache_clear = self.client.get(reverse("posts:index"))
        response_3 = response_after_cache_clear.content
        self.assertNotEqual(response_1, response_3)


class FollowTests(TestCase):
    def setUp(self):
        self.following_user = User.objects.create(username='Following')
        self.not_following_user = User.objects.create(username='Unfollowing')
        self.author = User.objects.create(username='author')

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.author,
        )

        self.following_user_client = Client()
        self.following_user_client.force_login(self.following_user)

        self.not_following_user_client = Client()
        self.not_following_user_client.force_login(self.not_following_user)

        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_follow(self):
        self.following_user_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))
        self.assertTrue(Follow.objects.filter(user=self.following_user,
                                              author=self.author).exists())
        self.following_user_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}))
        self.assertEqual(len(Follow.objects.filter(user=self.following_user,
                                                   author=self.author)), 1)
        self.following_user_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}))
        self.assertFalse(Follow.objects.filter(user=self.following_user,
                                               author=self.author).exists())

    def test_follow_feed(self):
        Follow.objects.get_or_create(author=self.author,
                                     user=self.following_user)
        response = self.following_user_client.get(
                       reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 1)
        response = self.not_following_user_client.get(
                       reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 0)
