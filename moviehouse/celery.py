from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviehouse.settings')
app = Celery('moviehouse')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.timezone = settings.TIME_ZONE
app.conf.enable_utc = False   # !!!important for crontab

app.conf.beat_schedule = {
    'check-sessions-periodically': {
        'task': 'staff.tasks.sessions_checker',
        'schedule': 15.0,
        'args': ()
    },
}


#COMMANDS
#celery -A moviehouse worker --loglevel=INFO
#celery -A moviehouse beat -l info
