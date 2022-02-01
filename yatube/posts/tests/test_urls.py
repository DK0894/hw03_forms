from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class UserURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        Post.objects.create(
            author=User.objects.create_user(username='auth'),
            text='test_text'
        )

    def setUp(self):
        # Создан неавторизованный клиент
        self.guest_client = Client()
        # Создан пользователь
        self.user = User.objects.create_user(username='Test_username')
        # Создан второй клиент
        self.authorized_client = Client()
        # Авторизация пользователя
        self.authorized_client.force_login(self.user)

    # def test_main_page(self):
    #     """Страница / доступна любому пользователю."""
    #     # Отправляем запрос через client,
    #     # созданный в setUp()
    #     response = self.guest_client.get('/')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_group_list_page(self):
    #     """Страница /group/slug/ доступна любому пользователю."""
    #     response = self.guest_client.get('/group/test_slug/')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_profile_page(self):
    #     """Страница /profile/username/ доступна любому пользователю."""
    #     response = self.guest_client.get('/profile/Test_username/')
    #     self.assertEqual(response.status_code, 200)
    #
    # def test_post_detail_page(self):
    #     """Страница /posts/post_id/ доступна любому пользователю."""
    #     response = self.guest_client.get('posts/test_id/')
    #     self.assertEqual(response.status_code, 200)

    def test_some_pages_for_guest_clients(self):
        """Страницы доступны любому пользователю."""
        url_path = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/Test_username/': HTTPStatus.OK,
            f'/posts/{1}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, status_page in url_path.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, status_page)
