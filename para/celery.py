import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'para.settings')


import django
django.setup()

from  celery import Celery 
from django.conf import settings



app = Celery('para')

# settings.configure()
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace = 'CELERY')


# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# Optional: Add this for periodic tasks with django-celery-beat
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'