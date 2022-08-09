from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView

from cinema.models import Genre, Hall, Movie, MovieSessionSettings, MovieSession
from staff.forms import GenreCreateForm, HallCreateForm


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = 'login/'

    def test_func(self):
        return self.request.user.is_superuser


class MainView(SuperUserRequiredMixin, TemplateView):
    template_name = 'admin.html'


class GenreListView(SuperUserRequiredMixin, ListView):
    model = Genre
    template_name = 'staff-genre-list.html'
    extra_context = {'create_form': GenreCreateForm()}


class GenreCreateView(SuperUserRequiredMixin, CreateView):
    http_method_names = ['post']
    template_name = 'staff-genre-edit.html'
    form_class = GenreCreateForm
    success_url = reverse_lazy('genre')


class GenreDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genre')


class GenreUpdateView(LoginRequiredMixin, UpdateView):
    model = Genre
    template_name = 'staff-genre-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('genre')


class HallListView(SuperUserRequiredMixin, ListView):
    model = Hall
    template_name = 'staff-hall-list.html'
    extra_context = {'create_form': HallCreateForm()}


class HallCreateView(SuperUserRequiredMixin, CreateView):
    http_method_names = ['post']
    template_name = 'staff-hall-edit.html'
    form_class = HallCreateForm
    success_url = reverse_lazy('hall')


class HallDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Hall
    success_url = reverse_lazy('hall')


class HallUpdateView(LoginRequiredMixin, UpdateView):
    model = Hall
    template_name = 'staff-hall-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('hall')


class MovieListView(SuperUserRequiredMixin, ListView):
    model = Movie
    template_name = 'staff-movie-list.html'
    paginate_by = 10


class MovieCreateView(SuperUserRequiredMixin, CreateView):
    model = Movie
    template_name = 'staff-movie-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('movie-list')


class MovieDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Movie
    success_url = reverse_lazy('movie-list')


class MovieUpdateView(LoginRequiredMixin, UpdateView):
    model = Movie
    template_name = 'staff-movie-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('movie-list')


class MovieSessionSettingsListView(SuperUserRequiredMixin, ListView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-list.html'
    paginate_by = 10


class MovieSessionSettingsCreateView(SuperUserRequiredMixin, CreateView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('settings-list')


class MovieSessionSettingsDeleteView(SuperUserRequiredMixin, DeleteView):
    model = MovieSessionSettings
    success_url = reverse_lazy('settings-list')


class MovieSessionSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('settings-list')


class MovieSessionsListView(SuperUserRequiredMixin, ListView):
    model = MovieSession
    template_name = 'staff-movie-session-list.html'
    paginate_by = 30

    def get_queryset(self):
        movie = self.request.GET.get('filter_movie', '')
        hall = self.request.GET.get('filter_hall', '')
        time_start = self.request.GET.get('time_start', '')
        time_end = self.request.GET.get('time_end', '')
        date_start = self.request.GET.get('date_start', '')
        date_end = self.request.GET.get('date_end', '')
        order = self.request.GET.get('orderby', '')

        new_context = self.model.objects.filter(date__gte=timezone.now(),
                                        settings__time_start__gte=timezone.now())

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

        return new_context

    def get_context_data(self, **kwargs):
        context = super(MovieSessionsListView, self).get_context_data(**kwargs)
        context['unique_halls'] = self.get_queryset().order_by('settings__hall').distinct('settings__hall')
        context['unique_movies'] = self.get_queryset().order_by('settings__movie').distinct('settings__movie')
        return context

