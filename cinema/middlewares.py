from datetime import timedelta

from django.contrib.auth import logout
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

from moviehouse.settings import MINUTES_TO_LOGOUT_IF_INACTIVE


class CustomUserActivityCheckerMiddleware(MiddlewareMixin):
    """To logout inactive users"""
    def process_request(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            last_activity_at = cache.get('last_request')
            if last_activity_at:
                if timezone.now() > (last_activity_at + timedelta(minutes=MINUTES_TO_LOGOUT_IF_INACTIVE)):
                    logout(request)
            cache.set('last_request', timezone.now())
