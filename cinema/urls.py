from django.urls import path, include
from cinema.views import IndexView, LoginView, RegisterView, LogoutView, AccountView
from cinema.views import ScheduleView, ContactView, AboutView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('account/', AccountView.as_view(), name='account'),
    path('schedule/', ScheduleView.as_view(), name='schedule'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('about/', AboutView.as_view(), name='about'),

]