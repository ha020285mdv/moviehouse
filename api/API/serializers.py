import datetime

from django.utils import timezone
from rest_framework import serializers

from cinema.models import Genre, Movie, Hall, Order, CinemaUser
from cinema.models import MovieSession, MovieSessionSettings


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class HallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hall
        fields = '__all__'


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


class MovieSessionSerializer(serializers.ModelSerializer):
    movie = serializers.CharField(source='settings.movie.title', read_only=True)
    hall = serializers.CharField(source='settings.hall.name', read_only=True)
    time_start = serializers.TimeField(source='settings.time_start', read_only=True)
    time_end = serializers.TimeField(source='settings.time_end', read_only=True)
    price = serializers.IntegerField(source='settings.price', read_only=True)

    class Meta:
        model = MovieSession
        fields = ['id', 'date', 'time_start', 'time_end', 'movie', 'hall', 'price']


class MovieSessionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSessionSettings
        fields = '__all__'

    def validate(self, data):
        hall = data['hall']
        start = data.get('date_start', timezone.now().date())
        end = data['date_end']

        # avoid date end < start
        if start < timezone.now().date():
            raise serializers.ValidationError({'date_start': 'Can not create sessions for past'})
        # avoid date end < start

        if end < start:
            raise serializers.ValidationError("Date end can not be less than date start")

        time_start = data['time_start']
        time_end = data['time_end']

        # avoid time end < start
        if time_end <= time_start:
            raise serializers.ValidationError("Time end can not be less than time start or equal")

        # avoid creating sessions crossed by hall same date same time
        sessions = MovieSessionSettings.objects.filter(hall=hall)
        if self.instance:
            sessions = sessions.exclude(pk=self.instance.pk)
        for session in sessions:
            cross_days = (session.date_start <= start <= session.date_end) or (
                        session.date_start <= end <= session.date_end)
            cross_hours = (session.time_start <= time_start <= session.time_end) or (
                        session.time_start <= time_end <= session.time_end)
            if cross_days and cross_hours:
                raise serializers.ValidationError(f"Session crosses at least with session id#{session.pk}")

        return data


class CinemaUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CinemaUser
        fields = ['id', 'email', 'password', 'first_name']

    def create(self, validated_data):
        user = CinemaUser.objects.create(email=validated_data['email'],
                                         username=validated_data['email'],
                                         first_name=validated_data['first_name'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(read_only=True)
    session = serializers.IntegerField(write_only=True)
    sits = serializers.ListField(child=serializers.IntegerField(min_value=1))

    class Meta:
        model = Order
        fields = '__all__'

    def validate(self, data):
        sits = data['sits']
        session = MovieSession.objects.get(pk=data['session'])
        start = datetime.datetime.combine(session.date, session.settings.time_start)
        list_of_free = session.free_sits.values_list('number', flat=True)
        string_of_free = ', '.join(str(x) for x in list_of_free)

        for sit in sits:
            if not (1 <= sit <= session.settings.hall.hall_capacity):
                raise serializers.ValidationError(
                    {'sits': f'Sit has to be positive number from list of free sits at this time: {string_of_free}.'})
            if sit not in list_of_free:
                raise serializers.ValidationError(
                    {'sits': f'One or more sits from your order are not free already. '
                     f'Free numbers at this time: {string_of_free}.'})

        if len(sits) > len(set(sits)):
            raise serializers.ValidationError({'sits': 'Sits are duplicated'})

        if timezone.now() > start:
            raise serializers.ValidationError('Current session is already expired.')

        return data
