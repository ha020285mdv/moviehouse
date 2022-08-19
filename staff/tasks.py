from celery import Celery
from celery import shared_task
from django.utils.timezone import now


broker_url = 'redis://localhost'
app = Celery('tasks', broker=broker_url, backend=broker_url)


@shared_task
def running_session():

    return f'Task one has done {now()}'
