#backend/config/celery.py
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("faq_project")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.enable_utc = False
app.conf.timezone = 'Europe/Amsterdam'

# Celery Beat schedule
app.conf.beat_schedule = {
    "weekly-download-job": {
        "task": "download_and_process",
        "schedule": crontab(minute=45, hour=15, day_of_week=2),  # Every Monday at 10:50 PM
        "options": {"expires": 9000},  #expires in 2.5 hour
    },
}
