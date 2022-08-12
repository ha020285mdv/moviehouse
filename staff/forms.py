from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone

from cinema.models import Movie, Genre, Hall, Order
from cinema.models import MovieSessionSettings


class GenreCreateForm(ModelForm):
    class Meta:
        model = Genre
        fields = '__all__'


class HallCreateForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'


class HallUpdateForm(ModelForm):
    class Meta:
        model = Hall
        fields = '__all__'

    def clean(self):
        if Order.objects.filter(session__settings__hall=self.instance):
            raise ValidationError("Can't edit: hall already in orders")


class MovieUpdateForm(ModelForm):
    class Meta:
        model = Movie
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['advertised'] and not \
                (cleaned_data['trailer'] and cleaned_data['teaser'] and cleaned_data['img_landscape']):
            raise ValidationError("Media data are required for advertising")

        if Order.objects.filter(session__settings__movie=self.instance):
            raise ValidationError("Can't edit: movie already ordered")


class SettingsCreateForm(ModelForm):
    class Meta:
        model = MovieSessionSettings
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        # avoid updating sessions which already ordered
        if self.instance and Order.objects.filter(session__settings=self.instance):
            raise ValidationError("Can't edit: sessions already in orders")

        hall = cleaned_data['hall']
        date_start = cleaned_data['date_start']
        date_end = cleaned_data['date_end']
        # avoid date end < start
        if date_start < timezone.now().date():
            raise ValidationError("Can not create sessions for past")
        # avoid date end < start
        if date_end < date_start:
            raise ValidationError("Date end can not be less than date start")
        time_start = cleaned_data['time_start']
        time_end = cleaned_data['time_end']
        # avoid time end < start
        if time_end <= time_start:
            raise ValidationError("Time end can not be less than time start")

        # avoid creating sessions crossed by hall same date same time
        sessions = MovieSessionSettings.objects.filter(hall=hall)
        if self.instance:
            sessions = sessions.exclude(pk=self.instance.pk)     # to exclude instance while updating existed object
        for session in sessions:
            cross_days = (session.date_start <= date_start <= session.date_end) or (session.date_start <= date_end <= session.date_end)
            cross_hours = (session.time_start <= time_start <= session.time_end) or (session.time_start <= time_end <= session.time_end)
            if cross_days and cross_hours:
                raise ValidationError(f"Session crosses at least with session id#{session.pk}")
