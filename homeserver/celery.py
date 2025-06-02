import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homeserver.settings')

# Windows specific settings
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('homeserver')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Windows doesn't support the 'prefork' pool, so we use 'solo' instead
app.conf.update(
    worker_pool_restarts=True,
    worker_concurrency=1,  # Reduce concurrency for Windows
    broker_connection_retry_on_startup=True,
    task_acks_late=True,
    worker_lost_wait=30.0,
    worker_pool='solo',  # Use solo pool for Windows
)

# Fix for Windows event loop policy
if os.name == 'nt':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
