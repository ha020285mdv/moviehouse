import datetime

from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.utils import timezone

from cinema.models import CinemaUser, Order, MovieSession, Sit


class CustomUserCreationForm(UserCreationForm):

    class Meta(UserCreationForm):
        model = CinemaUser
        fields = ('email', 'first_name')

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.username = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ()

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(OrderForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        sits = self.request.POST.getlist("sit")
        sits_set = Sit.objects.filter(id__in=sits)
        session = MovieSession.objects.get(pk=self.request.POST.get("session"))
        start = datetime.datetime.combine(session.date, session.settings.time_start)

        if timezone.now() > start:
            raise ValidationError('Current session is already expired.')

        for sit in sits_set:
            if sit not in session.free_sits:
                raise ValidationError(f'Sit #{sit.number} from your order are not free already. Please choose new.')
