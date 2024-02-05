import os

from celery import Celery

from core.settings import TTL_DELETE_SCHEDULE_TIME

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY", force=True)
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "delete by ttl": {"task": "converter.clear_by_ttl", "schedule": TTL_DELETE_SCHEDULE_TIME},
}
