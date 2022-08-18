from datetime import datetime, date
import random
from datetime import timedelta
from faker import Faker
import factory
from django.utils import timezone
from cinema.models import CinemaUser, Genre, Movie, Hall, MovieSessionSettings

fake = Faker()


class UserFactory(factory.Factory):
    email = factory.Sequence(lambda n: 'user%d@gmail.com' % n)
    username = email
    first_name = fake.name()
    password = 'topsecret007'

    class Meta:
        model = CinemaUser


class SuperUserFactory(UserFactory):
    is_superuser = True


class GenreFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'genre%d' % n)

    class Meta:
        model = Genre


class MovieFactory(factory.Factory):
    title = factory.Sequence(lambda n: 'movie%d' % n)
    description = fake.text()
    director = factory.Faker('name')
    starring = f'{fake.name()}, {fake.name()}, {fake.name()}'
    age_policy = random.choice([1, 2, 3])

    class Meta:
        model = Movie


class HallFactory(factory.Factory):
    name = factory.Sequence(lambda n: 'hall%d' % n)
    sits_rows = 6
    sits_cols = 10

    class Meta:
        model = Hall


class MovieSessionSettingsFactory(factory.Factory):
    hall = HallFactory()
    movie = MovieFactory()
    price = factory.LazyAttribute(random.randrange(1, 50))
    date_start = factory.LazyFunction(datetime.now)
    date_end = factory.LazyFunction(datetime.now)
    time_start = '12:00'
    time_end = '14:00'

    class Meta:
        model = MovieSessionSettings
