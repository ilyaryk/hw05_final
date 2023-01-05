from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = Group.objects.create(
            title='test-title',
            slug='test-slug',
            description='test-description'
        )

        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user,
            group=self.group,
        )

    def test_public_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': self.group.slug}),
            'posts/posts.html': reverse('posts:post_detail',
                                        kwargs={'post_id': self.post.id}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username':
                                                  self.user.username})
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_authorized_urls_uses_correct_templates(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_author_urls_uses_correct_templates(self):
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_404_url_uses_correct_template(self):
        response = self.authorized_client.get('/non-existent-page/')
        self.assertTemplateUsed(response, 'core/404.html')

    def test_nonexistent_page(self):
        '''Не работает с несуществующеми адресами'''
        response = self.authorized_client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, 404)
        response = self.client.get('/nonexistent_page/')
        self.assertEqual(response.status_code, 404)

    def test_authorized_only_create(self):
        '''Только авторизованный может создавать посты'''
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_author_only_edit(self):
        '''Редактировать может только автор'''
        self.authorized_client_not_author = Client()
        self.user_2 = User.objects.create_user(username='HasNoName2')
        self.authorized_client_not_author.force_login(self.user_2)
        response = self.guest_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
        response = self.authorized_client_not_author.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 302)
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, 200)

    def test_authorized_only_comment(self):
        '''Комменировать может только авторизированный'''
        response = self.guest_client.get(f'/posts/{self.post.id}/comment')
        self.assertEqual(response.status_code, 301)
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)
