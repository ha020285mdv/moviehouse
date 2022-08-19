from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
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

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Hall(models.Model):
    name = models.CharField(max_length=100, unique=True)
    sits_rows = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    sits_cols = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    @property
    def hall_capacity(self):
        return self.sits_cols * self.sits_rows

    def __str__(self):
        return f'{self.name} {self.hall_capacity} sits'


class MovieSession(models.Model):
    settings = models.ForeignKey('MovieSessionSettings', on_delete=CASCADE)
    date = models.DateField()

    class Meta:
        ordering = ['date']

    @property
    def free_sits(self):
        return Sit.objects.filter(session=self, order__isnull=True)

    @property
    def free_sits_number(self):
        return len(self.free_sits)

    @property
    def sold(self):
         return self.settings.hall.hall_capacity - self.free_sits_number

    def __str__(self):
        return f'{self.settings.hall.name}: {self.date} ' \
               f'{self.settings.time_start} - "{self.settings.movie.title[:20]}..."'


class MovieSessionSettings(models.Model):
    hall = models.ForeignKey(Hall, on_delete=CASCADE)
    movie = models.ForeignKey(Movie, on_delete=CASCADE)
    date_start = models.DateField(default=timezone.now)
    date_end = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    price = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        ordering = ['-date_start']

    def save(self, **kwargs):
        if self.id:
            MovieSession.objects.filter(settings=self).delete()
        super().save(**kwargs)
        delta = self.date_end - self.date_start
        for day in range(delta.days + 1):
            session = MovieSession.objects.create(settings=self, date=self.date_start + timezone.timedelta(days=day))
            seats = []
            for sit in range(1, self.hall.hall_capacity + 1):
                seats.append(Sit(session=session, number=sit))
            Sit.objects.bulk_create(seats)

    def __str__(self):
        return f'{self.movie} ({self.hall.name}) {self.date_start} to ' \
               f'{self.date_end} ({self.time_start}-{self.time_end}) {self.price}$'



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
    datetime = models.DateTimeField(auto_now=True)
    sits = models.ForeignKey('Sit', on_delete=CASCADE)

    class Meta:
        ordering = ['datetime']

    def __str__(self):
        return f'{self.customer} #{self.sits.number} for {self.datetime}'


class Sit(models.Model):
    session = models.ForeignKey(MovieSession, on_delete=CASCADE)
    number = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['session', 'number']
