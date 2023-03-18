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
    url_user_register = reverse('usermanager:user-register')
    url_user_login = reverse('usermanager:user-login')

    def setUp(self):
        return super().setUp()

    def create_test_user(self):
        data = deepcopy(self.data)
        data.pop('contacts', [])
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
        тест RegisterAccount проверка - незаполненные данные.
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

