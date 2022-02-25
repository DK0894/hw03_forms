from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from ..forms import PostForm
from django import forms

from ..models import Group, Post

User = get_user_model()


class UserFormCreateTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='auth'),
            text='test_text',
            group=UserFormCreateTest.group,
        )
        cls.form = PostForm()

    def setUp(self):
        # Создаем неавторизованный пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user = User.objects.create_user(username='Test_username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': f'{self.post.text}',
            'group': f'{self.post.group.title}',
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', args={self.post.author.username})
                             )
        # Проверяем, увеличелось ли число постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверяем, что создалась запись с заданным post_id
        self.assertTrue(
            Post.objects.filter(
                post_id=self.post.pk,
                text='test_text',
                group='test_group',
            ).exists()
        )
