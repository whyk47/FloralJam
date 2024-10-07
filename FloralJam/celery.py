import os

from django.conf import settings

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FloralJam.settings')

app = Celery(
    'FloralJam',
    broker_url="sqs://",
    broker_transport_options={
        "region": "ap-southeast-1",
        "predefined_queues": {
            "celery": {  ## the name of the SQS queue
                "url": os.environ.get("SQS_QUEUE_URL"),
                "access_key_id": os.environ.get("AWS_ACCESS_KEY"),
                "secret_access_key": os.environ.get("AWS_SECRET_KEY"),
            }
        },
    },
    task_create_missing_queues=False,
)   

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(f'django.conf.settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')