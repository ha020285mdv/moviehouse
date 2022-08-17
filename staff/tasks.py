from celery import Celery
from celery import shared_task
from django.db import transaction
from django.utils.timezone import now


broker_url = 'redis://localhost'
app = Celery('tasks', broker=broker_url, backend=broker_url)


@shared_task
def task_one():
    return f'Task one has done {now()}'


@shared_task
def task_two():
    return f'Task two has done at {now()}'

@shared_task
def add(x, y):
    return x + y
