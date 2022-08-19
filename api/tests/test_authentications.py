from datetime import timedelta
from rest_framework.authtoken.models import Token
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework.test import APITestCase

from cinema.tests.factories import UserFactory
from moviehouse.settings import MINUTES_DRF_TOKEN_LIFE_TIME


class TokenAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.user.save()
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_token_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(self.token))
        response = self.client.get(f'/api/users/')
        self.assertEqual(response.status_code, 200)

    def test_wrong_token_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format('wrongtoken'))
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 401)

    def test_expired_token_auth(self):
        token, _ = Token.objects.get_or_create(user=self.user)
        token.created = token.created - timedelta(minutes=(MINUTES_DRF_TOKEN_LIFE_TIME+1))
        token.save()
        self.client.credentials(HTTP_AUTHORIZATION='Token {}'.format(token))
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, 401)
