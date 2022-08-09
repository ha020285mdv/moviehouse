from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DetailView

from cinema.forms import CustomUserCreationForm, OrderForm
from cinema.models import CinemaUser, Movie, MovieSession, Order


class IndexView(ListView):
    template_name = 'index.html'
    paginate_by = 10
    queryset = Movie.objects.filter(advertised=True)
    context_object_name = 'movies'


class LoginView(LoginView):
    success_url = '/'
    template_name = 'login.html'

    def get_success_url(self):
        return self.success_url


class RegisterView(CreateView):
    model = CinemaUser
    form_class = CustomUserCreationForm
    success_url = '/'
    template_name = 'register.html'

    def form_valid(self, form):
        to_return = super().form_valid(form)
        login(self.request, self.object)
        msg = 'You have been successfully registered and logged in!'
        messages.success(self.request, msg)
        return to_return


class LogoutView(LoginRequiredMixin, LogoutView):
    success_url = '/'


class AccountView(TemplateView):
    template_name = 'account.html'


class ScheduleView(TemplateView):
    template_name = 'schedule.html'


class ContactView(TemplateView):
    template_name = 'contact.html'


class AboutView(TemplateView):
    template_name = 'about.html'


class MovieView(DetailView):
    model = Movie
    template_name = 'movie.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['today_sessions'] = MovieSession.objects.filter(settings__movie=self.object,
                                                        date=timezone.now(),
                                                        settings__time_start__gt=timezone.now())
        next_day = timezone.now() + timedelta(1)
        context['tomorrow_sessions'] = MovieSession.objects.filter(settings__movie=self.object, date=next_day)
        context['all_sessions'] = MovieSession.objects.filter(settings__movie=self.object,
                                                      date__gte=timezone.now())

        return context


class SessionView(DetailView):
    model = MovieSession
    template_name = 'session.html'
    extra_context = {'orderform': OrderForm}

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_sessions'] = MovieSession.objects.filter(settings__movie=self.object.settings.movie,
                                                              date__gte=timezone.now())
        cols = self.object.settings.hall.sits_cols
        rows = self.object.settings.hall.sits_rows
        context['last_col_sits'] = [rows * col for col in range(1, cols+1)]
        return context


class OrderView(CreateView):
    form_class = OrderForm
    success_url = 'account'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request=request)
        if form.is_valid():
            sits = dict.fromkeys(request.POST.getlist("sit", []), True)
            session = MovieSession.objects.get(pk=request.POST.get("session"))
            Order.objects.create(customer=self.request.user,
                                 session=session,
                                 sits=sits)
            session.sits.update(sits)
            session.save()
            return redirect('account')
        else:
            return redirect(self.request.META.get('HTTP_REFERER'), {'orderform': form})

    def form_invalid(self, form):
        # # Whatever you wanna do. This example simply reloads the list
        # self.object_list = self.get_queryset()
        # context = self.get_context_data(task_form=form)
        # return self.render_to_response(context)
        return redirect(self.request.META.get('HTTP_REFERER'), {'orderform': form})
