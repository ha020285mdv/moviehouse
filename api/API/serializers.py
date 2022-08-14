from rest_framework import serializers

from cinema.models import Genre, Movie, Hall, MovieSession, MovieSessionSettings, Order, CinemaUser


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
    class Meta:
        model = MovieSession
        fields = '__all__'


class MovieSessionSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieSessionSettings
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


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
