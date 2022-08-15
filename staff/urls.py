from django.urls import path
from staff.views import MainView, MovieSessionsStaffListView
from staff.views import GenreListView, GenreCreateView, GenreDeleteView, GenreUpdateView
from staff.views import MovieSessionSettingsUpdateView, MovieSessionSettingsDeleteView
from staff.views import MovieSessionSettingsListView, MovieSessionSettingsCreateView
from staff.views import MovieListView, MovieCreateView, MovieDeleteView, MovieUpdateView
from staff.views import HallListView, HallCreateView, HallDeleteView, HallUpdateView
from staff.views import MovieSessionsListView

urlpatterns = [
    path('main/', MainView.as_view(), name='main'),

    path('main/genre/', GenreListView.as_view(), name='genre'),
    path('main/genre/create/', GenreCreateView.as_view(), name='genre-create'),
    path('main/genre/delete/<int:pk>/', GenreDeleteView.as_view(), name='genre-delete'),
    path('main/genre/edit/<int:pk>/', GenreUpdateView.as_view(), name='genre-edit'),

    path('main/hall/', HallListView.as_view(), name='hall'),
    path('main/hall/create/', HallCreateView.as_view(), name='hall-create'),
    path('main/hall/delete/<int:pk>/', HallDeleteView.as_view(), name='hall-delete'),
    path('main/hall/edit/<int:pk>/', HallUpdateView.as_view(), name='hall-edit'),

    path('main/movie-list/', MovieListView.as_view(), name='movies'),
    path('main/movie/create/', MovieCreateView.as_view(), name='movie-create'),
    path('main/movie/delete/<int:pk>/', MovieDeleteView.as_view(), name='movie-delete'),
    path('main/movie/edit/<int:pk>/', MovieUpdateView.as_view(), name='movie-edit'),

    path('main/session-settings-list/', MovieSessionSettingsListView.as_view(), name='settings-list'),
    path('main/session-settings/create/', MovieSessionSettingsCreateView.as_view(), name='settings-create'),
    path('main/session-settings/delete/<int:pk>/', MovieSessionSettingsDeleteView.as_view(), name='settings-delete'),
    path('main/session-settings/edit/<int:pk>/', MovieSessionSettingsUpdateView.as_view(), name='settings-edit'),

    path('main/sessions-list/', MovieSessionsStaffListView.as_view(), name='sessions-list'),
]