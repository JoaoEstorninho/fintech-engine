from celery import Celery
from app.core.config import settings

celery_app = Celery("worker")

if settings.ENV == "test":
    celery_app.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
        broker_url="memory://",
        result_backend="cache+memory://",
    )
else:
    celery_app.conf.update(
        broker_url="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
    )