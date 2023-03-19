from copy import deepcopy

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from .models import User


class APITests(APITestCase):
    """
    Класс для тестирования работы views
    """

    data = {
        'first_name': 'Some_first_name',
        'last_name': 'Some_last_name',
        'email': 'some_mail@ya.ru',
        'password': 'some_pass',
        'company': 'Company',
        'position': 'Pos',

    }
    url_user_register = reverse('user-register')
    url_user_login = reverse('user-login')

    def setUp(self):
        return super().setUp()

    def create_test_user(self):
        data = deepcopy(self.data)
        password = data.pop('password')

        user = User.objects.create(**data, type='buyer')
        user.is_active = True
        user.set_password(password)
        user.save()

    def test_user_registration(self):
        """
        тест RegisterAccount,проверка статуса ответа.
        """

        response = self.client.post(self.url_user_register, self.data)

        assert response.status_code == 201
        assert response.data['Status'] is True

    def test_user_reg_empty(self):
        """
        тест RegisterAccount проверка - незаполненные данные,
        при регистрации
        """

        data = deepcopy(self.data)
        data.pop('email')

        response = self.client.post(self.url_user_register, data)

        assert 'Errors' in response.data
        assert response.data['Errors'] == 'необходимо заполнить все обязательные поля'
        assert response.status_code == 401

    def test_user_reg_valid(self):
        """
        тест RegisterAccount проверка парамеров на валидацию при регистации user.
        """

        data = deepcopy(self.data)
        data['email'] = ''

        response = self.client.post(self.url_user_register, data)

        assert response.status_code == 422
        assert response.data['Status'] is False
        assert 'Errors' in response.data

    def test_new_user_registration_password_error(self):
        """
        тест RegisterAccount проверка пароля
        """

        data = deepcopy(self.data)
        data['password'] = ''
        response = self.client.post(self.url_user_register, data)

        assert response.status_code == 403
        assert response.data['Status'] is False
        assert 'Errors' in response.data

    def test_login_account(self):
        """
        views LoginAccount,
        проверка статуса авторизации
        """

        self.create_test_user()
        email = self.data['email']
        password = self.data['password']
        login_data = dict(email=email, password=password)
        response = self.client.post(self.url_user_login, login_data)

        assert response.status_code is 200
        assert 'Status' in response.data
        assert response.data['Status'] is True

    def test_login_empty_data(self):
        """
        views LoginAccount проверка заполнения обязательных полей
        при авторизации
        """

        self.create_test_user()
        email = self.data['email']
        password = self.data['password']
        login_data = dict(email=email, password=password)
        login_data.pop('email')

        response = self.client.post(self.url_user_login, login_data)

        assert self.failureException == AssertionError
        assert response.status_code == 401

    def test_get_contact(self):
        """ views ContactView test метода get на отсутсвие Errors в данных
        ответа.
        """

        url_contact = reverse('user-contact')

        self.create_test_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        response = self.client.get(url_contact, format='json')

        assert response.status_code == 200
        assert 'Errors' not in response.data

    def test_get_contact_anon(self):
        """
        views ContactView test метода get на проверку выполнения запроса неавторизованым пользователем,
        наличие в данных ответа Errors.
        """

        url_contact = reverse('user-contact')
        response = self.client.get(url_contact, format='json')

        assert response.status_code == 403
        assert response.data['Status'] is False
        assert 'Error' in response.data

    def test_contact_post(self):
        """ views ContactView проверка метода post
        Проверяет код HTTP-статуса,отсутсвие Errors в данных ответа.
        """

        url_contact = reverse('user-contact')

        self.create_test_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {
            "city": "SomeCity",
            "street": "AnyStreet",
            "house": "999",
            "structure": "99",
            "building": "9",
            "apartment": "9898",
            "phone": "8-999-888-77-66"
        }

        response = self.client.post(url_contact, data=data)

        assert response.status_code == 201
        assert response.data['Status'] is True
        assert 'Error' not in response.data

    def test_post_contact_empty_data(self):
        """ views ContactView проверка метода post при незаполненных полях
        Проверяет код HTTP-статуса,наличие Errors в данных ответа.
        """

        url_contact = reverse('user-contact')

        self.create_test_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {
            "city": "SomeCity",
            "street": "AnyStreet",
            "structure": "99",
            "building": "9",
            "phone": "8-999-888-77-66"
        }

        response = self.client.post(url_contact, data=data, format='json')

        assert response.status_code == 401
        assert response.data['Status'] is False
        assert 'Error' not in response.data

    def test_delete_contact(self):
        """ views ContactView Проверка метода delete .
        Проверяет status_code и наличие статуса True в данных ответа.
        """

        url_contact = reverse('user-contact')

        self.create_test_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {"items": "10"}

        response = self.client.delete(url_contact, data=data, format='json')

        assert response.status_code == 200

    def test_delete_contact_empty_data(self):
        """ views ContactView проверка метода delete при незаполненных полях
        Проверяет соответсвие status_code коду 404,
        """

        url_contact = reverse('user-contact')

        self.create_test_user()
        email = self.data['email']
        user = User.objects.get(email=email)
        token = Token.objects.get_or_create(user_id=user.id)[0].key
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

        data = {"items": ''}

        response = self.client.delete(url_contact, data=data, format='json')

        assert response.status_code == 400

