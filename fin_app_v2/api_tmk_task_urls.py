# fast_urls.py
from django.urls import path
from . import api_tmk_task

urlpatterns = [
    # Fast Job URLs
    path('fast/jobs/', api_tmk_task.jobs_api, name='fast-jobs'),
    path('fast/jobs/<int:pk>/', api_tmk_task.job_detail_api, name='fast-job-detail'),
    path('fast/jobs/<int:pk>/tasks/', api_tmk_task.job_tasks_api, name='fast-job-tasks'),

    # Fast Task URLs
    path('fast/tasks/', api_tmk_task.tasks_api, name='fast-tasks'),
    path('fast/tasks/<int:pk>/', api_tmk_task.task_detail_api, name='fast-task-detail'),
]
