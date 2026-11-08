from celery import Celery
from app.config import REDIS_URL

celery_app = Celery(
    "zhi_zip",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.compress_task", "app.tasks.decompress_task"],
)

celery_app.conf.update(
    task_track_started=True,
    result_expires=3600,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
)

celery = celery_app
