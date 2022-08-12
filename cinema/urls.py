from django.urls import path
from cinema.views import IndexView, LoginView, RegisterView, LogoutView, AccountView
from cinema.views import SessionView, OrderView, MovieSessionsListView
from cinema.views import ContactView, AboutView, MovieView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('schedule/', MovieSessionsListView.as_view(), name='schedule'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('about/', AboutView.as_view(), name='about'),
    path('movie/<int:pk>/', MovieView.as_view(), name='movie'),
    path('session/<int:pk>/', SessionView.as_view(), name='session'),
    path('order/', OrderView.as_view(), name='order'),

]