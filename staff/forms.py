from django.forms import ModelForm
from cinema.models import Movie, Genre, Hall
from cinema.models import MovieSessionSettings


class GenreCreateForm(ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class HallCreateForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'
