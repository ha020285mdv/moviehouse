import json
from unittest import TestCase
from datetime import datetime, timedelta
from django.utils import timezone

from rest_framework.test import APIClient

from api.API.serializers import MovieSessionSerializer, OrderSerializer
from cinema.models import MovieSessionSettings, MovieSession, Sit, Order
from cinema.tests.factories import SuperUserFactory, UserFactory, HallFactory, MovieFactory


class MovieSessionViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.admin = SuperUserFactory()
        self.admin.save()
        self.user = UserFactory()
        self.user.save()

        hall = HallFactory(sits_rows=5, sits_cols=5)
        hall.save()
        movie = MovieFactory()
        movie.save()

        setting = MovieSessionSettings(hall=hall,
                                       movie=movie,
                                       price=20,
                                       date_start=(datetime.now().date() - timedelta(days=5)),
                                       date_end=(datetime.now().date() + timedelta(days=5)),
                                       time_start='18:00',
                                       time_end='21:00')
        setting.save()

        self.data = {}

    def test_get_sessions(self):
        response = self.client.get('/api/sessions/')
        self.assertEqual(response.status_code, 200)

    def test_get_sessions_data(self):
        response = self.client.get('/api/sessions/')
        queryset = MovieSession.objects.filter(date__gte=timezone.now())\
            .exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        serializer = MovieSessionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['results'], serializer.data)

    def test_get_sessions_data_todays_action(self):
        response = self.client.get('/api/sessions/todays/')
        queryset = MovieSession.objects.filter(date=timezone.now(), settings__time_start__gt=timezone.now())
        serializer = MovieSessionSerializer(queryset, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)


class MovieSessionSettingsViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.save()
        self.admin = SuperUserFactory()
        self.admin.save()
        self.client.force_authenticate(user=self.admin)

        self.hall = HallFactory(sits_rows=5, sits_cols=5)
        self.hall.save()
        self.hall2 = HallFactory(sits_rows=6, sits_cols=8)
        self.hall2.save()
        self.movie = MovieFactory()
        self.movie.save()

        self.setting = MovieSessionSettings(hall=self.hall,
                                            movie=self.movie,
                                            price=20,
                                            date_start=(datetime.now().date() - timedelta(days=5)),
                                            date_end=(datetime.now().date() + timedelta(days=5)),
                                            time_start='18:00',
                                            time_end='21:00')
        self.setting.save()

        sessions = self.setting.moviesession_set.all()
        one_session = sessions.get(date=datetime.now().date()+timedelta(days=1))
        self.sit = Sit.objects.get(session=one_session, number=7)

        self.data = {"date_start": datetime.now().date() + timedelta(days=1),
                     "date_end": datetime.now().date() + timedelta(days=10),
                     "time_start": "13:00",
                     "time_end": "15:00",
                     "price": 12,
                     "hall": self.hall.pk,
                     "movie": self.movie.pk
                     }

    def test_create_settings(self):
        response = self.client.post('/api/sessionsettings/', data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['id'],
                         MovieSessionSettings.objects.all().order_by('id').last().pk)

    def test_delete_settings(self):
        response = self.client.delete(f'/api/sessionsettings/{self.setting.pk}/')
        self.assertEqual(response.status_code, 204)

    def test_delete_settings_decline_if_ordered(self):
        order = Order.objects.create(customer=self.user, sits=self.sit)
        order.save()
        response = self.client.delete(f'/api/sessionsettings/{self.setting.pk}/')
        self.assertEqual(response.status_code, 400)

    def test_update_settings(self):
        self.data['hall'] = self.hall2.pk
        response = self.client.put(f'/api/sessionsettings/{self.setting.pk}/', data=self.data, format='json')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['hall'], MovieSessionSettings.objects.get(pk=self.setting.pk).hall.pk)

    def test_update_settings_decline_if_ordered(self):
        order = Order.objects.create(customer=self.user, sits=self.sit)
        order.save()
        self.data['hall'] = self.hall2.pk
        response = self.client.put(f'/api/sessionsettings/{self.setting.pk}/', data=self.data, format='json')
        self.assertEqual(response.status_code, 400)


class OrderViewSetTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.user.save()
        self.user2 = UserFactory()
        self.user2.save()
        self.admin = SuperUserFactory()
        self.admin.save()

        self.hall = HallFactory(sits_rows=5, sits_cols=5)
        self.hall.save()
        self.hall2 = HallFactory(sits_rows=6, sits_cols=8)
        self.hall2.save()
        self.movie = MovieFactory()
        self.movie.save()

        self.setting = MovieSessionSettings(hall=self.hall,
                                            movie=self.movie,
                                            price=20,
                                            date_start=(datetime.now().date() - timedelta(days=5)),
                                            date_end=(datetime.now().date() + timedelta(days=5)),
                                            time_start='18:00',
                                            time_end='21:00')
        self.setting.save()

        sessions = self.setting.moviesession_set.all()
        self.session = sessions.get(date=datetime.now().date()+timedelta(days=1))
        self.sit7 = Sit.objects.get(session=self.session, number=7)
        self.sit8 = Sit.objects.get(session=self.session, number=8)

        Order.objects.create(customer=self.user, sits=self.sit7)
        Order.objects.create(customer=self.user2, sits=self.sit8)

        self.data = {"session": self.session.pk, "sits": [5, 6]}

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/orders/', data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        sits = Sit.objects.filter(session=self.session, number__in=self.data['sits'])
        self.assertTrue(Order.objects.filter(sits__in=sits).exists())

    def get_orders_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        expected_qs = Order.objects.all()
        serializer = OrderSerializer(expected_qs, many=True)
        self.assertEqual(response.data, serializer.data)

    def get_orders_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/orders/')
        self.assertEqual(response.status_code, 200)
        expected_qs = Order.objects.filter(customer=self.user)
        serializer = OrderSerializer(expected_qs, many=True)
        self.assertEqual(response.data, serializer.data)
