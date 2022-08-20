from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView

from cinema.models import Genre, Hall, Movie, MovieSessionSettings, MovieSession, Order
from cinema.views import MovieSessionsListView
from staff.forms import GenreCreateForm, HallCreateForm, HallUpdateForm, MovieUpdateForm, \
    SettingsCreateForm


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    login_url = reverse_lazy('login')

    def test_func(self):
        return self.request.user.is_superuser


class MainView(SuperUserRequiredMixin, TemplateView):
    template_name = 'admin.html'
    extra_context = {'title': 'Main | Admin Popcorn cinema'}



class GenreListView(SuperUserRequiredMixin, ListView):
    model = Genre
    template_name = 'staff-genre-list.html'
    extra_context = {'title': 'Genres | Admin Popcorn cinema', 'create_form': GenreCreateForm()}


class GenreCreateView(SuperUserRequiredMixin, CreateView):
    http_method_names = ['post']
    template_name = 'staff-genre-edit.html'
    form_class = GenreCreateForm
    success_url = reverse_lazy('genre')
    extra_context = {'title': 'Genre create | Admin Popcorn cinema'}


class GenreDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genre')


class GenreUpdateView(LoginRequiredMixin, UpdateView):
    model = Genre
    template_name = 'staff-genre-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('genre')
    extra_context = {'title': 'Genre update | Admin Popcorn cinema'}


class HallListView(SuperUserRequiredMixin, ListView):
    model = Hall
    template_name = 'staff-hall-list.html'
    extra_context = {'title': 'Halls | Admin Popcorn cinema', 'create_form': HallCreateForm()}

    def get_context_data(self, **kwargs):
        context = super(HallListView, self).get_context_data(**kwargs)
        context['ordered'] = [hall for hall in Hall.objects.all() if Order.objects.filter(sits__session__settings__hall=hall)]
        return context


class HallCreateView(SuperUserRequiredMixin, CreateView):
    http_method_names = ['post']
    template_name = 'staff-hall-edit.html'
    form_class = HallCreateForm
    success_url = reverse_lazy('hall')
    extra_context = {'title': 'Hall create | Admin Popcorn cinema'}



class HallDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Hall
    success_url = reverse_lazy('hall')


class HallUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'staff-hall-edit.html'
    model = Hall
    form_class = HallUpdateForm
    success_url = reverse_lazy('hall')
    extra_context = {'title': 'Hall update | Admin Popcorn cinema'}


class MovieListView(SuperUserRequiredMixin, ListView):
    model = Movie
    template_name = 'staff-movie-list.html'
    paginate_by = 10
    extra_context = {'title': 'Movies | Admin Popcorn cinema'}

    def get_context_data(self, **kwargs):
        context = super(MovieListView, self).get_context_data(**kwargs)
        context['ordered'] = [movie for movie in Movie.objects.all() if
                              Order.objects.filter(sits__session__settings__movie=movie)]
        return context


class MovieCreateView(SuperUserRequiredMixin, CreateView):
    model = Movie
    template_name = 'staff-movie-edit.html'
    form_class = MovieUpdateForm
    success_url = reverse_lazy('allmovies')
    extra_context = {'title': 'Movie create | Admin Popcorn cinema'}


class MovieDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Movie
    success_url = reverse_lazy('allmovies')


class MovieUpdateView(LoginRequiredMixin, UpdateView):
    model = Movie
    template_name = 'staff-movie-edit.html'
    form_class = MovieUpdateForm
    success_url = reverse_lazy('allmovies')
    extra_context = {'title': 'Movie update | Admin Popcorn cinema'}


class MovieSessionSettingsListView(SuperUserRequiredMixin, ListView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-list.html'
    paginate_by = 10
    extra_context = {'title': 'Session settings | Admin Popcorn cinema'}

    def get_context_data(self, **kwargs):
        context = super(MovieSessionSettingsListView, self).get_context_data(**kwargs)
        context['ordered'] = [setting for setting in MovieSessionSettings.objects.all() if
                              Order.objects.filter(sits__session__settings=setting)]
        return context


class MovieSessionSettingsCreateView(SuperUserRequiredMixin, CreateView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-edit.html'
    form_class = SettingsCreateForm
    success_url = reverse_lazy('settings-list')
    extra_context = {'title': 'Setting create | Admin Popcorn cinema'}


class MovieSessionSettingsDeleteView(SuperUserRequiredMixin, DeleteView):
    model = MovieSessionSettings
    success_url = reverse_lazy('settings-list')


class MovieSessionSettingsUpdateView(LoginRequiredMixin, UpdateView):
    model = MovieSessionSettings
    template_name = 'staff-movie-session-settings-edit.html'
    form_class = SettingsCreateForm
    success_url = reverse_lazy('settings-list')
    extra_context = {'title': 'Setting update | Admin Popcorn cinema'}


class MovieSessionsStaffListView(SuperUserRequiredMixin, MovieSessionsListView):
    template_name = 'staff-movie-session-list.html'
    extra_context = {'title': 'Movies | Admin Popcorn cinema'}
