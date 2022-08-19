from datetime import datetime, timedelta
from unittest import TestCase

from django.utils import timezone

from api.API.serializers import MovieSessionSettingsSerializer, CinemaUserSerializer, OrderSerializer
from cinema.models import MovieSessionSettings, CinemaUser, Order, Sit
from cinema.tests.factories import HallFactory, MovieFactory, UserFactory


class MovieSessionSettingsSerializerTest(TestCase):
    def setUp(self):
        self.serializer = MovieSessionSettingsSerializer
        self.hall = HallFactory()
        self.hall.save()
        movie = MovieFactory()
        movie.save()

        self.setting = MovieSessionSettings(hall=self.hall,
                                            movie=movie,
                                            price=20,
                                            date_start=datetime.now().date(),
                                            date_end=(datetime.now().date()+timedelta(days=5)),
                                            time_start='18:00',
                                            time_end='21:00')
        self.setting.save()

        self.data_dict = {'date_end': timezone.now().date() + timedelta(5),
                          'time_start': '12:00',
                          'time_end': '14:00',
                          'price': 9,
                          'hall': self.hall.pk,
                          'movie': movie.pk
                          }

    def test_serializer_ok(self):
        serializer = self.serializer(data=self.data_dict)
        self.assertTrue(serializer.is_valid())

    def test_serializer_date_start_after_end(self):
        self.data_dict['date_start'] = timezone.now().date() + timedelta(5)
        self.data_dict['date_end'] = timezone.now().date() + timedelta(3)
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_date_start_in_past(self):
        self.data_dict['date_start'] = timezone.now().date() - timedelta(5)
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_time_start_less_time_end(self):
        self.data_dict['time_start'] = '12:00'
        self.data_dict['time_end'] = '11:00'
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_sessions_crosses(self):
        self.data_dict['time_start'] = '19:00'
        self.data_dict['time_end'] = '22:00'
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_updating_session(self):
        self.data_dict['time_start'] = '19:00'
        self.data_dict['time_end'] = '22:00'
        serializer = self.serializer(instance=self.setting, data=self.data_dict)
        self.assertTrue(serializer.is_valid())


class CinemaUserSerializerTest(TestCase):
    def setUp(self):
        self.serializer = CinemaUserSerializer

    def test_serializer_user_create(self):
        data_dict = {'email': 'super@gmail.com',
                     'password': 'ya01neskagu',
                     'first_name': 'super'}
        serializer = self.serializer(data=data_dict)
        serializer.is_valid()
        serializer.save()
        self.assertTrue(CinemaUser.objects.filter(email='super@gmail.com').exists())


class OrderSerializerTest(TestCase):
    def setUp(self):
        self.serializer = OrderSerializer

        customer = UserFactory()
        customer.save()

        hall = HallFactory(sits_rows=5, sits_cols=5)
        hall.save()
        movie = MovieFactory()
        movie.save()

        setting = MovieSessionSettings(hall=hall,
                                       movie=movie,
                                       price=20,
                                       date_start=(datetime.now().date()-timedelta(days=5)),
                                       date_end=(datetime.now().date()+timedelta(days=5)),
                                       time_start='18:00',
                                       time_end='21:00')
        setting.save()

        sessions = setting.moviesession_set.all()
        self.past_session = sessions.get(date=datetime.now().date()-timedelta(days=3))
        actual_session = sessions.get(date=datetime.now().date()+timedelta(days=1))

        self.sit = Sit.objects.get(session=actual_session, number=7)
        order = Order.objects.create(customer=customer, sits=self.sit)
        order.save()

        self.data_dict = {'sits': [5, 6],
                          'session': actual_session.pk
                          }

    def test_serializer_ok(self):
        serializer = self.serializer(data=self.data_dict)
        self.assertTrue(serializer.is_valid())

    def test_serializer_session_expired(self):
        self.data_dict['session'] = self.past_session
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_sits_duplicate(self):
        self.data_dict['sits'] = [5, 5, 6]
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_sits_do_not_exist_in_hall(self):
        self.data_dict['sits'] = [40, -1]
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())

    def test_serializer_sits_already_sold(self):
        self.data_dict['sits'] = [self.sit.number]
        serializer = self.serializer(data=self.data_dict)
        self.assertFalse(serializer.is_valid())
