import os

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pzserver.settings')

app = Celery('orchestration')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html
app.conf.beat_schedule = {
    "check-finish": {
        "task": "core.tasks.check_processes_finish",
        "schedule": 60.0,
    },
}
app.conf.timezone = "UTC"

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')