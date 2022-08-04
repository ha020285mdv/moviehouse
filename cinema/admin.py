from django.contrib import admin
from cinema.models import Genre, Movie, Hall, MovieSessionSettings, MovieSession, CinemaUser, Order


admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(Hall)
admin.site.register(MovieSessionSettings)
admin.site.register(MovieSession)
admin.site.register(CinemaUser)
admin.site.register(Order)
