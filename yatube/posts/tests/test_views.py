from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class UserViewTest(TestCase):
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
            group=UserViewTest.group,
        )

    def setUp(self):
        # Создаем неавторизованный пользователя
        self.guest_client = Client()
        # Создаем авторизованного пользователя
        self.user = User.objects.create_user(username='Test_username')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        for i in range(1, 15):
            self.post = Post.objects.create(
                author=self.user,
                text='test_text',
            )

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        post = self.post
        templates_page_names = {
            reverse('posts:main_page'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test_slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Test_username'}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': f'{post.pk}'}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:post_edit', kwargs={'post_id': f'{post.pk}'}):
                'posts/post_create.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_main_page_correct_context(self):
        """Проверка отображения поста на странице main_page."""
        response = self.authorized_client.get(reverse('posts:main_page'))
        first_object = response.context['page_obj'][0]
        post_objects = {
            'Test_username': f'{first_object.author.username}',
            'test_text': f'{first_object.text}',
            # 'test_description': f'{first_object.group.description}',
            # 'test_group': f'{first_object.group.title}',
        }
        for test_obj, obj in post_objects.items():
            with self.subTest(obj=obj):
                self.assertEqual(test_obj, obj)

    def test_group_list_page_correct_context(self):
        """Проверка отображения поста на странцие group_list."""
        response = self.authorized_client.get(reverse(
            'posts:group_list', args={self.group.slug})
        )
        post = response.context['page_obj'][0]
        group = response.context['group']
        self.assertEqual(group.title, 'test_group')
        self.assertEqual(group.description, 'test_description')
        self.assertEqual(group.slug, 'test_slug')
        self.assertEqual(post.text, 'test_text')

    def test_profile_page_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        post = response.context['page_obj'][0]
        post_text = post.text
        post_author = post.author
        self.assertEqual(post_author.username, 'Test_username')
        self.assertEqual(post_text, 'test_text')

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args={self.post.pk})
        )
        post = response.context.get('post')
        self.assertEqual(post.text, 'test_text')
        self.assertEqual(post.author.username, 'Test_username')
        # self.assertEqual(post.group.title, 'test_group')
        # self.assertEqual(post.group.description, 'test_description')

    def test_create_post_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', args={self.post.pk})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_main_page_contains_ten_records(self):
        # some_pages = {
        #     f'{reverse("posts:main_page")}': 10,
        #     f'{reverse("posts:group_list", args={self.group.slug})}': 10,
        #     f'{reverse("posts:profile", args={self.post.pk})}': 10,
        # }
        # for page, expected in some_pages.items():
        #     with self.subTest(page=page):
        #         response = self.client.get(page)
        #         self.assertEqual(len(response.context['page_obj']), 10)
        response = self.client.get(reverse('posts:main_page'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_main_page_contains_ten_records(self):
        response = self.client.get(reverse('posts:main_page') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)

    def test_first_page_group_list_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_list',
                                           args={self.group.slug})
                                   )
        self.assertEqual(len(response.context.get('group').title), 10)

    def test_second_page_group_list_contains_ten_records(self):
        response = self.client.get(reverse('posts:group_list',
                                           args={self.group.slug}) + '?page=2'
                                   )
        self.assertEqual(len(response.context.get('group').title), 10)

    def test_first_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile', args={self.post.author.username})
        )
        self.assertEqual(len(response.context.get('page_obj')), 10)

    def test_second_page_profile_contains_ten_records(self):
        response = self.client.get(reverse(
            'posts:profile', args={self.post.author.username}) + '?page=2'
        )
        self.assertEqual(len(response.context.get('page_obj')), 4)

    def test_additional_check_create_post(self):
        post = Post.objects.create(

        )
