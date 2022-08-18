from datetime import datetime, date, timedelta
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.test import TestCase, RequestFactory
from django.urls import reverse

from cinema.models import Hall, Order, MovieSessionSettings, Sit, Movie
from cinema.views import IndexView
from cinema.tests.factories import UserFactory, SuperUserFactory, HallFactory, MovieFactory
from staff.views import HallListView, MovieListView, MovieSessionSettingsListView


class HallListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.user.save()
        self.superuser = SuperUserFactory()

        self.hall1 = HallFactory()
        self.hall1.save()
        self.hall2 = HallFactory()
        self.hall2.save()

        self.movie = MovieFactory()
        self.movie.save()
        self.movie_other = MovieFactory()
        self.movie_other.save()

        self.setting = MovieSessionSettings(hall=self.hall1,
                                            movie=self.movie,
                                            price=25,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.setting_other = MovieSessionSettings(hall=self.hall2,
                                                  movie=self.movie_other,
                                                  price=20,
                                                  date_start=(datetime.now() - timedelta(days=3)),
                                                  date_end=(datetime.now() + timedelta(days=3)),
                                                  time_start='15:00',
                                                  time_end='17:00')
        self.setting_other.save()

        sits = Sit.objects.filter(session__settings=self.setting)

        self.order1 = Order.objects.create(customer=self.user, sits=sits[0])
        self.order2 = Order.objects.create(customer=self.user, sits=sits[1])
        self.order3 = Order.objects.create(customer=self.user, sits=sits[2])


    def test_availability_non_auth(self):
        request = self.factory.get(reverse('hall'))
        request.user = AnonymousUser()
        response = HallListView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_availability_user_auth(self):
        request = self.factory.get(reverse('hall'))
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            self.assertRaises(PermissionDenied, HallListView.as_view()(request))

    def test_availability_superuser(self):
        request = self.factory.get(reverse('hall'))
        request.user = self.superuser
        response = HallListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_ordered(self):
        request = self.factory.get(reverse('hall'))
        request.user = self.superuser
        response = HallListView.as_view()(request)
        context = response.context_data
        ordered_halls = [hall for hall in Hall.objects.all() if
                         Order.objects.filter(sits__session__settings__hall=hall)]
        self.assertIn('ordered', context)
        self.assertEqual(context['ordered'], ordered_halls)


class MovieListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.user.save()
        self.superuser = SuperUserFactory()

        self.hall1 = HallFactory()
        self.hall1.save()
        self.hall2 = HallFactory()
        self.hall2.save()

        self.movie = MovieFactory()
        self.movie.save()
        self.movie_other = MovieFactory()
        self.movie_other.save()

        self.setting = MovieSessionSettings(hall=self.hall1,
                                            movie=self.movie,
                                            price=25,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.setting_other = MovieSessionSettings(hall=self.hall2,
                                                  movie=self.movie_other,
                                                  price=20,
                                                  date_start=(datetime.now() - timedelta(days=3)),
                                                  date_end=(datetime.now() + timedelta(days=3)),
                                                  time_start='15:00',
                                                  time_end='17:00')
        self.setting_other.save()

        sits = Sit.objects.filter(session__settings=self.setting)

        self.order1 = Order.objects.create(customer=self.user, sits=sits[0])
        self.order2 = Order.objects.create(customer=self.user, sits=sits[1])
        self.order3 = Order.objects.create(customer=self.user, sits=sits[2])


    def test_availability_non_auth(self):
        request = self.factory.get(reverse('movies'))
        request.user = AnonymousUser()
        response = MovieListView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_availability_user_auth(self):
        request = self.factory.get(reverse('movies'))
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            self.assertRaises(PermissionDenied, MovieListView.as_view()(request))

    def test_availability_superuser(self):
        request = self.factory.get(reverse('movies'))
        request.user = self.superuser
        response = MovieListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_ordered(self):
        request = self.factory.get(reverse('movies'))
        request.user = self.superuser
        response = MovieListView.as_view()(request)
        context = response.context_data
        ordered_halls = [movie for movie in Movie.objects.all() if
                         Order.objects.filter(sits__session__settings__movie=movie)]
        self.assertIn('ordered', context)
        self.assertEqual(context['ordered'], ordered_halls)


class MovieSessionSettingsListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()
        self.user.save()
        self.superuser = SuperUserFactory()

        self.hall1 = HallFactory()
        self.hall1.save()
        self.hall2 = HallFactory()
        self.hall2.save()

        self.movie = MovieFactory()
        self.movie.save()
        self.movie_other = MovieFactory()
        self.movie_other.save()

        self.setting = MovieSessionSettings(hall=self.hall1,
                                            movie=self.movie,
                                            price=25,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.setting_other = MovieSessionSettings(hall=self.hall2,
                                                  movie=self.movie_other,
                                                  price=20,
                                                  date_start=(datetime.now() - timedelta(days=3)),
                                                  date_end=(datetime.now() + timedelta(days=3)),
                                                  time_start='15:00',
                                                  time_end='17:00')
        self.setting_other.save()

        sits = Sit.objects.filter(session__settings=self.setting)

        self.order1 = Order.objects.create(customer=self.user, sits=sits[0])
        self.order2 = Order.objects.create(customer=self.user, sits=sits[1])
        self.order3 = Order.objects.create(customer=self.user, sits=sits[2])


    def test_availability_non_auth(self):
        request = self.factory.get(reverse('settings-list'))
        request.user = AnonymousUser()
        response = MovieSessionSettingsListView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_availability_user_auth(self):
        request = self.factory.get(reverse('settings-list'))
        request.user = self.user
        with self.assertRaises(PermissionDenied):
            self.assertRaises(PermissionDenied, MovieSessionSettingsListView.as_view()(request))

    def test_availability_superuser(self):
        request = self.factory.get(reverse('settings-list'))
        request.user = self.superuser
        response = MovieSessionSettingsListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_ordered(self):
        request = self.factory.get(reverse('settings-list'))
        request.user = self.superuser
        response = MovieSessionSettingsListView.as_view()(request)
        context = response.context_data
        ordered_halls = [setting for setting in MovieSessionSettings.objects.all() if
                         Order.objects.filter(sits__session__settings=setting)]
        self.assertIn('ordered', context)
        self.assertEqual(context['ordered'], ordered_halls)

