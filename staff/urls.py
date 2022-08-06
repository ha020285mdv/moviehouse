from django.urls import path
from staff.views import MainView, GenreListView, GenreCreateView, GenreDeleteView, GenreUpdateView
from staff.views import MovieListView, MovieCreateView, MovieDeleteView, MovieUpdateView
from staff.views import HallListView, HallCreateView, HallDeleteView, HallUpdateView

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

    path('main/movie-list/', MovieListView.as_view(), name='movie-list'),
    path('main/movie/create/', MovieCreateView.as_view(), name='movie-create'),
    path('main/movie/delete/<int:pk>/', MovieDeleteView.as_view(), name='movie-delete'),
    path('main/movie/edit/<int:pk>/', MovieUpdateView.as_view(), name='movie-edit'),

]