#backend/config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("faq_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.timezone = 'Europe/Amsterdam'

# Celery Beat schedule
app.conf.beat_schedule = {
    "weekly-download-job": {
        "task": "async_download_pipeline",
        "task": "faq_api.tasks.async_download_and_process",
        "schedule": crontab(minute=50, hour=22, day_of_week=1),  # Every Monday at 10:50 PM
        "options": {"expires": 3600},  #expires in 1 hour
    },
}
