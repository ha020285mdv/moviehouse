from datetime import timedelta
from django.utils import timezone
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication
from moviehouse.settings import MINUTES_DRF_TOKEN_LIFE_TIME


class TokenWithLifeTimeAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key=key)
        if (token.created + timedelta(minutes=MINUTES_DRF_TOKEN_LIFE_TIME)) < timezone.now():
            token.delete()
            raise exceptions.AuthenticationFailed('Token is expired. Get new one.')
        return user, token
