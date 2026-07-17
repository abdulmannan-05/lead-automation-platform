from celery.result import AsyncResult
from app.workers.celery_app import celery_app

task_id = "26bdadf7-5def-4450-a5dc-9f26977ce85c"
result = AsyncResult(task_id, app=celery_app)

print(f"Status: {result.status}")
if result.ready():
    print("Task Finished!")
    print(f"Result: {result.result}")
else:
    print("Task is still running in the background...")