from django.contrib.auth.forms import UserCreationForm
from cinema.models import CinemaUser


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
