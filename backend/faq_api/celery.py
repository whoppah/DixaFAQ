#backend/faq_api/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("faq_api")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.enable_utc = False
app.conf.timezone = 'Europe/Amsterdam'

# Celery Beat schedule
app.conf.beat_schedule = {
    "weekly-download-job": {
        "task": "faq_api.tasks.start_pipeline",  
        "schedule": crontab(minute=25, hour=11, day_of_week=3),  # Every Monday at 7:00 AM
    },
}
