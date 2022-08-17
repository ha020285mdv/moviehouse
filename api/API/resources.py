from django.db import transaction
from django.utils import timezone
from rest_framework import mixins, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet

from api.API.filters import SessionsFilter
from api.API.permissions import IsAdminOrReadOnly, IsAdminOrCreateOnlyOrReadOwnForOrder, \
    IsAdminOrCreateOnlyForUsers
from api.API.serializers import GenreSerializer, MovieSerializer, HallSerializer, MovieSessionSerializer
from api.API.serializers import MovieSessionSettingsSerializer, OrderSerializer, CinemaUserSerializer
from cinema.models import Genre, Movie, Hall, Order, CinemaUser, Sit
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
    filter_backends = [SessionsFilter, ]

    def get_queryset(self):
        return MovieSession.objects.filter(date__gte=timezone.now())\
            .exclude(date=timezone.now(), settings__time_start__lte=timezone.now())

    @action(detail=False, methods=['get'])
    def todays(self, request):
        queryset = self.get_queryset().filter(date=timezone.now(), settings__time_start__gt=timezone.now())
        queryset = self.filter_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class MovieSessionSettingsViewSet(ModelViewSet):
    queryset = MovieSessionSettings.objects.all()
    serializer_class = MovieSessionSettingsSerializer
    permission_classes = (IsAdminUser, )

    def perform_create(self, serializer, obj=None):
        start = serializer.validated_data.get('date_start', timezone.now().date())
        end = serializer.validated_data.get('date_end')
        delta = end - start
        setting = serializer.save(date_start=start)
        for day in range(delta.days + 1):
            session = MovieSession.objects.create(settings=setting, date=start + timezone.timedelta(days=day))
            for sit in range(1, setting.hall.hall_capacity + 1):
                Sit.objects.create(session=session, number=sit)

    def perform_destroy(self, instance):
        if Order.objects.filter(session__settings=instance):
            raise serializers.ValidationError("Can't delete: sessions already in orders")
        instance.delete()

    def perform_update(self, serializer):
        obj = self.get_object()
        if Order.objects.filter(session__settings=obj):
            raise serializers.ValidationError("Can't update: sessions already in orders")
        MovieSession.objects.filter(settings=obj).delete()
        self.perform_create(serializer)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAdminOrCreateOnlyOrReadOwnForOrder, )

    def get_queryset(self):
        return self.queryset if self.request.user.is_superuser else self.queryset.filter(customer=self.request.user)

    def perform_create(self, serializer):
        sits = serializer.validated_data.get('sits')
        session = serializer.validated_data.get('session')
        for sit in sits:
            Order.objects.create(customer=self.request.user, sits=Sit.objects.get(session=session, number=int(sit)))


class UserViewSet(ModelViewSet):
    queryset = CinemaUser.objects.all()
    serializer_class = CinemaUserSerializer
    permission_classes = (IsAdminOrCreateOnlyForUsers, )

    def get_queryset(self):
        return self.queryset if self.request.user.is_superuser else self.queryset.filter(pk=self.request.user.pk)
