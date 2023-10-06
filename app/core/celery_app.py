from celery import Celery, Task
from app.conf.config import settings


celery_app = Celery("worker", broker=settings.REDIS_URL)

celery_app.autodiscover_tasks([
    'app.contrib.account.tasks',
    'app.contrib.bundle.tasks',
    'app.contrib.wallet.tasks',
])




celery_app.conf.task_routes = {"app.worker.test_celery": "main-queue"}
