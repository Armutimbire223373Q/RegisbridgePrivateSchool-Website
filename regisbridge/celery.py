"""Celery configuration for the Regisbridge project."""
import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'regisbridge.settings')

# Create the Celery application
app = Celery('regisbridge')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure task routes
app.conf.task_routes = {
    'admissions.*': {'queue': 'admissions'},
    'blog.*': {'queue': 'blog'},
    'main.*': {'queue': 'main'},
}

# Configure task time limits
app.conf.task_time_limit = 60 * 5  # 5 minutes
app.conf.task_soft_time_limit = 60 * 3  # 3 minutes

# Configure task retries
app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f'Request: {self.request!r}')
