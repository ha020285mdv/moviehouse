from django.contrib import admin
from django.urls import path, include
from cinema.views import IndexView, LoginView, RegisterView, LogoutView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
]





