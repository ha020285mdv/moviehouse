from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.views.generic import TemplateView, CreateView, ListView

from cinema.forms import CustomUserCreationForm
from cinema.models import CinemaUser, Movie


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
