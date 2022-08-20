from celery import Celery
from cinema.models import MovieSession
from django.utils import timezone

import logging
from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

broker_url = 'redis://localhost'
app = Celery('tasks', broker=broker_url, backend=broker_url)


channel_layer = get_channel_layer()


@shared_task
def sessions_checker():
    current_sessions = MovieSession.objects.filter(date=timezone.now().date(),
                                                   settings__time_start__lte=timezone.now(),
                                                   settings__time_end__gte=timezone.now())
    async_to_sync(channel_layer.group_send)(
        "jokes", {"type": "jokes.joke", "text": current_sessions}
    )
    return f'Sessions running: {current_sessions}'
