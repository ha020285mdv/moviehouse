from datetime import datetime, date, timedelta

from django.contrib.auth.models import AnonymousUser
from django.db.models import Sum
from django.test import TestCase, RequestFactory, Client
from django.utils import timezone

from cinema.forms import CustomUserCreationForm
from cinema.models import CinemaUser, MovieSessionSettings, MovieSession, Order, Sit
from cinema.tests.factories import UserFactory, MovieFactory, GenreFactory, MovieSessionSettingsFactory, HallFactory
from cinema.views import IndexView, LoginView, AccountView, MovieView, SessionView, OrderView, MovieSessionsListView


class IndexViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_availability(self):
        request = self.factory.get('/')
        response = IndexView.as_view()(request)
        self.assertEqual(response.status_code, 200)


class LoginViewTest(TestCase):
    def setUp(self):
        self.c = Client()
        self.user = CinemaUser.objects.create(email='user1@gmail.com',
                                              username='user1@gmail.com',
                                              password='top_secret01',
                                              first_name='User')
        self.data = {'email': 'user1@gmail.com', 'password': 'top_secret01'}

    def test_availability(self):
        factory = RequestFactory()
        request = factory.get('/login')
        request.user = AnonymousUser()
        response = LoginView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_logged(self):
        response = self.c.post('/login/', self.data)
        self.assertEqual(response.status_code, 200)


class RegisterViewTest(TestCase):
    def setUp(self):
        self.form_data = {'email': 'bob@gmail.com',
                          'first_name': 'Bob',
                          'password1': 'j3hgGgd12n',
                          'password2': 'j3hgGgd12n'}
        self.c = Client()

    def test_register_redirect(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_register_user_created(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        self.assertTrue(CinemaUser.objects.filter(email='bob@gmail.com').exists())

    def test_register_user_logged(self):
        form = CustomUserCreationForm(data=self.form_data)
        form.is_valid()
        response = self.c.post('/register/', form.cleaned_data)
        from django.contrib import auth
        user = auth.get_user(self.c)
        assert user.is_authenticated


class AccountViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        hall = HallFactory()
        hall.save()

        movie = MovieFactory()
        movie.save()

        self.setting = MovieSessionSettings(hall=hall,
                                            movie=movie,
                                            price=20,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.customer1 = UserFactory()
        self.customer1.save()
        self.customer2 = UserFactory()
        self.customer2.save()

        self.order_sit1 = Order.objects.create(customer=self.customer1, sits=Sit.objects.all()[0])
        self.order_sit2 = Order.objects.create(customer=self.customer1, sits=Sit.objects.all()[1])
        self.order_sit3 = Order.objects.create(customer=self.customer2, sits=Sit.objects.all()[2])

    def test_decline_for_unauthorized(self):
        request = self.factory.get('/account')
        request.user = AnonymousUser()
        response = AccountView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_availability_for_authorized(self):
        request = self.factory.get('/account')
        request.user = self.customer1
        response = AccountView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_queryset(self):
        request = self.factory.get('/account')
        request.user = self.customer1
        response = AccountView.as_view()(request)
        view = AccountView()
        view.request = request
        qs = view.get_queryset()
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(qs, Order.objects.filter(customer=self.customer1))

    def test_get_context_data_count_of_orders(self):
        request = self.factory.get('/account')
        request.user = self.customer1
        response = AccountView.as_view()(request)
        context = response.context_data
        orders = Order.objects.filter(customer=self.customer1)
        self.assertIn('count', context)
        self.assertEqual(context['count'], len(orders))

    def test_get_context_data_sum_spent(self):
        request = self.factory.get('/account')
        request.user = self.customer1
        response = AccountView.as_view()(request)
        context = response.context_data
        orders = Order.objects.filter(customer=self.customer1)
        total_spent = orders.aggregate(Sum('sits__session__settings__price'))
        self.assertIn('sum', context)
        self.assertEqual(context['sum'], total_spent)


class MovieViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        hall = HallFactory()
        hall.save()

        self.movie = MovieFactory()
        self.movie.save()
        self.movie_other = MovieFactory()
        self.movie_other.save()

        self.customer1 = UserFactory()
        self.customer1.save()

        self.setting = MovieSessionSettings(hall=hall,
                                            movie=self.movie,
                                            price=20,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.setting_other = MovieSessionSettings(hall=hall,
                                                  movie=self.movie_other,
                                                  price=20,
                                                  date_start=(datetime.now() - timedelta(days=3)),
                                                  date_end=(datetime.now() + timedelta(days=3)),
                                                  time_start='15:00',
                                                  time_end='17:00')
        self.setting.save()


    def test_availability_for_unauthorized(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = AnonymousUser()
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        self.assertEqual(response.status_code, 200)

    def test_availability_for_authorized(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = self.customer1
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_title(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = self.customer1
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        context = response.context_data
        self.assertIn('title', context)
        self.assertEqual(context['title'], f'{self.movie.title} | Popcorn cinema')

    def test_get_context_data_today_sessions(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = self.customer1
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        context = response.context_data
        todays = MovieSession.objects.filter(settings__movie=self.movie,
                                             date=timezone.now(),
                                             settings__time_start__gt=timezone.now())
        self.assertIn('today_sessions', context)
        self.assertQuerysetEqual(context['today_sessions'], todays)

    def test_get_context_data_next_day_sessions(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = self.customer1
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        context = response.context_data
        next_day = timezone.now() + timedelta(1)
        tomorrow = MovieSession.objects.filter(settings__movie=self.movie,
                                               date=next_day)
        self.assertIn('tomorrow_sessions', context)
        self.assertQuerysetEqual(context['tomorrow_sessions'], tomorrow)

    def test_get_context_data_all_sessions(self):
        request = self.factory.get(f'/movie/{self.movie.pk}/')
        request.user = self.customer1
        response = MovieView.as_view()(request, **{'pk': self.movie.pk})
        context = response.context_data
        all_sessions = MovieSession.objects.filter(settings__movie=self.movie, date__gte=timezone.now())\
            .exclude(settings__movie=self.movie, date=timezone.now(), settings__time_start__lte=timezone.now())
        self.assertIn('all_sessions', context)
        self.assertQuerysetEqual(context['all_sessions'], all_sessions)


class SessionViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        hall = HallFactory()
        hall.save()

        self.movie = MovieFactory()
        self.movie.save()
        self.movie_other = MovieFactory()
        self.movie_other.save()

        self.customer1 = UserFactory()
        self.customer1.save()

        self.setting = MovieSessionSettings(hall=hall,
                                            movie=self.movie,
                                            price=20,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.setting_other = MovieSessionSettings(hall=hall,
                                                  movie=self.movie_other,
                                                  price=20,
                                                  date_start=(datetime.now() - timedelta(days=3)),
                                                  date_end=(datetime.now() + timedelta(days=3)),
                                                  time_start='15:00',
                                                  time_end='17:00')
        self.setting.save()
        self.session = MovieSession.objects.get(settings=self.setting,
                                                   date=(datetime.now()+timedelta(days=1)))

    def test_availability_for_unauthorized(self):
        request = self.factory.get(f'/session/{self.session.pk}/')
        request.user = AnonymousUser()
        response = SessionView.as_view()(request, **{'pk': self.session.pk})
        self.assertEqual(response.status_code, 200)

    def test_availability_for_authorized(self):
        request = self.factory.get(f'/session/{self.session.pk}/')
        request.user = self.customer1
        response = SessionView.as_view()(request, **{'pk': self.session.pk})
        self.assertEqual(response.status_code, 200)

    def test_get_context_data_all_sessions(self):
        request = self.factory.get(f'/session/{self.session.pk}/')
        request.user = self.customer1
        response = SessionView.as_view()(request, **{'pk': self.session.pk})
        context = response.context_data
        movie = self.session.settings.movie
        all_sessions = MovieSession.objects.filter(settings__movie=movie,
                                                   date__gte=timezone.now())\
            .exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        self.assertIn('all_sessions', context)
        self.assertQuerysetEqual(context['all_sessions'], all_sessions)

    def test_get_context_data_last_col_sits(self):
        request = self.factory.get(f'/session/{self.session.pk}/')
        request.user = self.customer1
        response = SessionView.as_view()(request, **{'pk': self.session.pk})
        context = response.context_data
        movie = self.session.settings.movie
        cols = self.session.settings.hall.sits_cols
        rows = self.session.settings.hall.sits_rows
        list_of_last_sits = [rows * col for col in range(1, cols + 1)]
        self.assertIn('last_col_sits', context)
        self.assertQuerysetEqual(context['last_col_sits'], list_of_last_sits)



class OrderViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

        hall = HallFactory()
        hall.save()

        movie = MovieFactory()
        movie.save()

        self.setting = MovieSessionSettings(hall=hall,
                                            movie=movie,
                                            price=20,
                                            date_start=(datetime.now()-timedelta(days=5)),
                                            date_end=(datetime.now()+timedelta(days=5)),
                                            time_start='12:00',
                                            time_end='14:00')
        self.setting.save()

        self.customer1 = UserFactory()
        self.customer1.save()
        self.customer2 = UserFactory()
        self.customer2.save()

        self.sit1 = Sit.objects.all()[0]
        self.sit2 = Sit.objects.all()[1]
        self.sit3 = Sit.objects.all()[2]

        self.c = Client()
        self.c.force_login(self.customer1)
        self.data = {"sit": [self.sit1.pk, self.sit2.pk], "session": self.sit2.session.pk}

    def test_decline_for_unauthorized(self):
        request = self.factory.get('/order')
        request.user = AnonymousUser()
        response = OrderView.as_view()(request)
        self.assertEqual(response.status_code, 302)

    def test_redirect_to_login_for_unauthorized(self):
        self.c.logout()
        response = self.c.post('/order', self.data)
        self.assertEqual(response.status_code, 301)

    def test_order_tickets(self):
        self.c.post('/order', self.data)
        orders_by_user = Order.objects.filter(customer=self.customer1)
        orders_by_sits = Order.objects.filter(sits__in=self.data['sit'])
        self.assertQuerysetEqual(orders_by_user, orders_by_sits)


class MovieSessionsListViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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

    def test_availability(self):
        request = self.factory.get('schedule/')
        response = MovieSessionsListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

    def test_get_filtered_by_movie(self):
        data = {'filter_movie': self.movie.title}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.filter(settings__movie__title=self.movie.title)
        self.assertQuerysetEqual(qs, expected_queryset)

    def test_get_filtered_by_hall(self):
        data = {'filter_hall': self.hall1.name}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.filter(settings__hall__name=self.hall1.name)
        self.assertQuerysetEqual(qs, expected_queryset)

    def test_get_filtered_by_time_start_time_end(self):
        time_start = '14:00'
        time_end = '18:00'
        data = {'time_start': time_start, 'time_end': time_end}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.filter(settings__time_start__gte=time_start,
                                             settings__time_start__lte=time_end)
        self.assertQuerysetEqual(qs, expected_queryset)

    def test_get_filtered_by_date_start_date_end(self):
        date_start = timezone.now().date() + timedelta(days=2)
        date_end = timezone.now().date() + timedelta(days=5)
        data = {'date_start': date_start, 'date_end': date_end}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.filter(date__gte=date_start,
                                             date__lte=date_end)
        self.assertQuerysetEqual(qs, expected_queryset)

    def test_get_ordered_by_price(self):
        data = {'orderprice': 'asc'}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.order_by('settings__price')
        self.assertEqual(qs[0], expected_queryset[0])
        self.assertEqual(qs[1], expected_queryset[1])


    def test_get_ordered_by_price_desc(self):
        data = {'orderprice': 'desc'}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.order_by('-settings__price')
        self.assertEqual(qs[0], expected_queryset[0])
        self.assertEqual(qs[1], expected_queryset[1])

    def test_get_ordered_by_time(self):
        data = {'ordertime': 'asc'}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.order_by('settings__time_start')
        self.assertEqual(qs[0], expected_queryset[0])
        self.assertEqual(qs[1], expected_queryset[1])

    def test_get_ordered_by_time_desc(self):
        data = {'ordertime': 'desc'}
        request = self.factory.get('schedule/', data)
        view = MovieSessionsListView()
        view.request = request
        qs = view.get_queryset()
        actual_qs = MovieSession.objects.filter(date__gte=timezone.now()).\
            exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        expected_queryset = actual_qs.order_by('-settings__time_start')
        self.assertEqual(qs[0], expected_queryset[0])
        self.assertEqual(qs[1], expected_queryset[1])

