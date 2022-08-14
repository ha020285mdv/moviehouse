from django.utils import timezone
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.API.permissions import IsAdminOrReadOnly, IsAdminOrCreateOnly, IsAdminOrCreateOnlyOrReadOwnForOrder, \
    IsAdminOrCreateOnlyForUsers
from api.API.serializers import GenreSerializer, MovieSerializer, HallSerializer, MovieSessionSerializer
from api.API.serializers import MovieSessionSettingsSerializer, OrderSerializer, CinemaUserSerializer
from cinema.models import Genre, Movie, Hall, Order, CinemaUser
from cinema.models import MovieSession, MovieSessionSettings


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly, )


class HallViewSet(ModelViewSet):
    queryset = Hall.objects.all()
    serializer_class = HallSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly, )


class MovieViewSet(ModelViewSet):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    permission_classes = (IsAdminOrReadOnly, )


class MovieSessionViewSet(ReadOnlyModelViewSet):
    queryset = MovieSession.objects.all()
    serializer_class = MovieSessionSerializer

    def get_queryset(self):
        return MovieSession.objects.filter(date__gte=timezone.now())\
            .exclude(date=timezone.now(), settings__time_start__lte=timezone.now())


class MovieSessionSettingsViewSet(ModelViewSet):
    queryset = MovieSessionSettings.objects.all()
    serializer_class = MovieSessionSettingsSerializer
    permission_classes = (IsAdminUser, )


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrCreateOnlyOrReadOwnForOrder, )

    def get_queryset(self):
        return self.queryset if self.request.user.is_superuser else self.queryset.filter(customer=self.request.user)

class UserViewSet(ModelViewSet):
    queryset = CinemaUser.objects.all()
    serializer_class = CinemaUserSerializer
    permission_classes = (IsAdminOrCreateOnlyForUsers, )

    def get_queryset(self):
        return self.queryset if self.request.user.is_superuser else self.queryset.filter(pk=self.request.user.pk)
