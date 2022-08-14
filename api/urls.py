from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views

from api.API.resources import GenreViewSet, HallViewSet, MovieViewSet, OrderViewSet, UserViewSet
from api.API.resources import MovieSessionViewSet, MovieSessionSettingsViewSet

router = routers.SimpleRouter()
router.register(r'genres', GenreViewSet)
router.register(r'halls', HallViewSet)
router.register(r'movies', MovieViewSet)
router.register(r'sessions', MovieSessionViewSet)
router.register(r'sessionsettings', MovieSessionSettingsViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'users', UserViewSet)


urlpatterns = [
    path('generate-token/', views.obtain_auth_token),
    path('', include(router.urls)),
]
