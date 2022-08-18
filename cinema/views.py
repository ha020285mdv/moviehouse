from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DetailView

from cinema.forms import CustomUserCreationForm, OrderForm
from cinema.models import CinemaUser, Movie, MovieSession, Order, Sit


class IndexView(ListView):
    template_name = 'index.html'
    paginate_by = 10
    model = Movie
    context_object_name = 'movies'

    def get_queryset(self):
        return self.model.objects.filter(advertised=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Head | Popcorn cinema'
        context['todays_sessions'] = MovieSession.objects.filter(date=timezone.now().date(),
                                                                 settings__time_start__gte=timezone.now()). \
            order_by('settings__time_start')
        context['tomorrows_sessions'] = MovieSession.objects.filter(date=(timezone.now() + timedelta(1))). \
            order_by('settings__time_start')

        # # calculating bestsellers
        # orders_last_30_days = Order.objects.filter(session__date__lte=timezone.now(),
        #                                            session__date__gte=(timezone.now() - timedelta(minutes=60*24*30)))
        # movies = {}
        # for order in orders_last_30_days:
        #     movies[order.session.settings.movie] = movies.get(order.session.settings.movie, 0) + len(order.sits)
        # context['bestsellers'] = {k: v for k, v in sorted(movies.items(), key=lambda item: item[1], reverse=True)}

        return context


class LoginView(LoginView):
    success_url = '/'
    template_name = 'login.html'
    extra_context = {'title': 'login | Popcorn cinema'}

    def get_success_url(self):
        msg = 'You have been successfully logged in!'
        messages.success(self.request, msg)
        return self.success_url


class RegisterView(CreateView):
    model = CinemaUser
    form_class = CustomUserCreationForm
    success_url = '/'
    template_name = 'register.html'
    extra_context = {'title': 'register | Popcorn cinema'}

    def form_valid(self, form):
        to_return = super().form_valid(form)
        login(self.request, self.object)
        msg = 'You have been successfully registered and logged in!'
        messages.success(self.request, msg)
        return to_return


class LogoutView(LoginRequiredMixin, LogoutView):
    success_url = '/'


class AccountView(LoginRequiredMixin, ListView):
    template_name = 'account.html'
    paginate_by = 20
    model = Order
    context_object_name = 'orders'
    extra_context = {'title': 'Account | Popcorn cinema'}

    def get_queryset(self):
        return self.model.objects.filter(customer=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(customer=self.request.user)
        context['count'] = len(orders)
        context['sum'] = orders.aggregate(Sum('sits__session__settings__price'))
        context['today'] = timezone.now().date()
        fresh_interval = timezone.now() - timedelta(minutes=15)
        context['recent_orders'] = Order.objects.filter(customer=self.request.user, datetime__gte=fresh_interval)
        return context


class MovieSessionsListView(ListView):
    model = MovieSession
    template_name = 'movie-session-list.html'
    paginate_by = 30
    extra_context = {'title': 'Schedule | Popcorn cinema'}

    def get_queryset(self):
        movie = self.request.GET.get('filter_movie')
        hall = self.request.GET.get('filter_hall')
        time_start = self.request.GET.get('time_start')
        time_end = self.request.GET.get('time_end')
        date_start = self.request.GET.get('date_start')
        date_end = self.request.GET.get('date_end')
        orderprice = self.request.GET.get('orderprice')
        ordertime = self.request.GET.get('ordertime')

        new_context = self.model.objects.filter(date__gte=timezone.now()).exclude(date=timezone.now(),
                                                                                  settings__time_start__lte=timezone.now())

        if movie:
            new_context = new_context.filter(settings__movie__title=movie)
        if hall:
            new_context = new_context.filter(settings__hall__name=hall)
        if time_start:
            new_context = new_context.filter(settings__time_start__gte=time_start)
        if time_end:
            new_context = new_context.filter(settings__time_start__lte=time_end)
        if date_start:
            new_context = new_context.filter(date__gte=date_start)
        if date_end:
            new_context = new_context.filter(date__lte=date_end)

        if orderprice == "asc":
            new_context = new_context.order_by('settings__price')
        elif orderprice == "desc":
            new_context = new_context.order_by('-settings__price')
        if ordertime == "asc":
            new_context = new_context.order_by('settings__time_start')
        elif ordertime == "desc":
            new_context = new_context.order_by('-settings__time_start')

        return new_context

    def get_context_data(self, **kwargs):
        context = super(MovieSessionsListView, self).get_context_data(**kwargs)
        qs = self.get_queryset()
        context['unique_halls'] = qs.order_by().distinct('settings__hall')
        context['unique_movies'] = qs.order_by().distinct('settings__movie')
        context['previous'] = self.request.GET
        return context


class ContactView(TemplateView):
    template_name = 'contact.html'
    extra_context = {'title': 'Contacts | Popcorn cinema'}


class AboutView(TemplateView):
    template_name = 'about.html'
    extra_context = {'title': 'About | Popcorn cinema'}


class MovieView(DetailView):
    model = Movie
    template_name = 'movie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title} | Popcorn cinema'
        context['today_sessions'] = MovieSession.objects.filter(settings__movie=self.object,
                                                                date=timezone.now(),
                                                                settings__time_start__gt=timezone.now()) \
            .order_by('settings__time_start')
        next_day = timezone.now() + timedelta(1)
        context['tomorrow_sessions'] = MovieSession.objects.filter(settings__movie=self.object, date=next_day) \
            .order_by('settings__time_start')
        context['all_sessions'] = MovieSession.objects.filter(settings__movie=self.object, date__gte=timezone.now())\
            .exclude(settings__movie=self.object, date=timezone.now(), settings__time_start__lte=timezone.now())\
            .order_by('date', 'settings__time_start')

        return context


class SessionView(DetailView):
    model = MovieSession
    template_name = 'session.html'
    extra_context = {'title': 'Order | Popcorn cinema', 'orderform': OrderForm}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_movie = self.get_object().settings.movie
        context['all_sessions'] = MovieSession.objects.filter(settings__movie=current_movie,
                                                              date__gte=timezone.now())\
            .exclude(date=timezone.now(), settings__time_start__lte=timezone.now())
        cols = self.object.settings.hall.sits_cols
        rows = self.object.settings.hall.sits_rows
        context['last_col_sits'] = [rows * col for col in range(1, cols + 1)]
        return context


class OrderView(LoginRequiredMixin, CreateView):
    form_class = OrderForm
    success_url = 'account'
    login_url = 'login'

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            messages.error(self.request, "Login, please, before order")
            return redirect('login')

        form = self.form_class(request.POST, request=request)
        if form.is_valid():
            sits = request.POST.getlist("sit", [])
            for sit in sits:
                Order.objects.create(customer=self.request.user, sits=Sit.objects.get(pk=sit))
            messages.success(self.request, "Your purchase is done. Tickets are in your account")
            return redirect('account')
        else:
            for msg in form.errors.as_data().get("__all__"):
                messages.error(self.request, msg.message)
            return redirect(self.request.META.get('HTTP_REFERER'), kwargs={'orderform': form})
