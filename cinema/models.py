from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import CASCADE
from django.utils import timezone

AGE_CHOICES = (
    (1, 'all'),
    (2, '13+'),
    (3, '18+')
)


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=300, unique=True)
    genres = models.ManyToManyField(Genre)
    description = models.TextField()
    director = models.CharField(max_length=100)
    starring = models.CharField(max_length=300)
    trailer = models.CharField(max_length=300, blank=True, null=True)
    teaser = models.CharField(max_length=300, blank=True, null=True)
    img_landscape = models.ImageField(upload_to='img/%Y/%m/%d', blank=True, null=True)
    img_standard = models.ImageField(upload_to='img/%Y/%m/%d', blank=True, null=True)
    img_small = models.ImageField(upload_to='img/%Y/%m/%d', blank=True, null=True)
    age_policy = models.PositiveSmallIntegerField(choices=AGE_CHOICES, default=1)
    advertised = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Hall(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sits_rows = models.PositiveSmallIntegerField()
    sits_cols = models.PositiveSmallIntegerField()

    @property
    def hall_capacity(self):
        return self.sits_cols * self.sits_rows

    def __str__(self):
        return f'{self.name} {self.hall_capacity} sits'


class MovieSession(models.Model):
    settings = models.ForeignKey('MovieSessionSettings', on_delete=CASCADE)
    date = models.DateField()
    sits = models.JSONField()

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.settings.hall.name}: {self.date} ' \
               f'{self.settings.time_start} - "{self.settings.movie.title[:20]}..."'





class MovieSessionSettings(models.Model):
    hall = models.ForeignKey(Hall, on_delete=CASCADE)
    movie = models.ForeignKey(Movie, on_delete=CASCADE)
    date_start = models.DateField(default=timezone.now().date(), validators=[MinValueValidator(timezone.now().date())])
    date_end = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    price = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['-date_start']

    def __str__(self):
        return f'{self.movie} ({self.hall.name}) {self.date_start} to ' \
               f'{self.date_end} ({self.time_start}-{self.time_end}) {self.price}$'

    # Может изменять зал или сеанс, если не было куплено ни одного билета в этот зал или на этот сеанс.
    def save(self, **kwargs):
        if self.id and True:    # check if empty
            MovieSession.objects.filter(settings=self).delete()
        super().save(**kwargs)
        delta = self.date_end - self.date_start
        for day in range(delta.days + 1):
            MovieSession.objects.create(settings=self,
                                        date=self.date_start + timezone.timedelta(days=day),
                                        sits={sit_number: False for sit_number in range(1, self.hall.hall_capacity + 1)}
                                        )


class CinemaUser(AbstractUser):
    email = models.EmailField(max_length=150, blank=False, unique=True)
    first_name = models.CharField(max_length=150, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        app_label = 'cinema'

    def __str__(self):
        return f'{self.first_name or self.email}'


class Order(models.Model):
    customer = models.ForeignKey(CinemaUser, on_delete=CASCADE)
    session = models.ForeignKey(MovieSession, on_delete=CASCADE)
    datetime = models.DateTimeField(auto_now=True)
    sits = models.JSONField()

    def __str__(self):
        return f'{self.customer} {len(self.sits)} sits in {self.datetime}'
