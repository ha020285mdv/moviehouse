from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView, ListView, DeleteView, UpdateView

from cinema.models import Genre, Hall, Movie
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
    http_method_names = ['post']
    model = Movie
    fields = '__all__'
    success_url = reverse_lazy('movie')


class MovieDeleteView(SuperUserRequiredMixin, DeleteView):
    model = Movie
    success_url = reverse_lazy('movie')


class MovieUpdateView(LoginRequiredMixin, UpdateView):
    model = Hall
    template_name = 'staff-movie-edit.html'
    fields = '__all__'
    success_url = reverse_lazy('movie')
