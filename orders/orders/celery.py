
import os
from celery import Celery

# Интеграция  в celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "orders.settings")
app = Celery("orders") #создаем экземпляр класса нашего django-приложения
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()