from django.urls import path
from . import api_views
from .api_jwt_email import EmailTokenObtainPairView
from .api_job_crud import (
    api_get_all_jobs, api_get_job_detail, api_update_job, api_delete_job, api_bulk_jobs
)
from .api_task_views import (
    api_get_all_tasks, api_get_task_detail, api_create_task,
    api_update_task, api_delete_task, api_get_task_statistics
)

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/email/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair_email'),

    # JOB CRUD — function-based views
    path('api/jobs/all/', api_get_all_jobs, name='job_all'),
    path('api/jobs/<int:job_id>/', api_get_job_detail, name='job_detail'),
    path('api/jobs/<int:job_id>/update/', api_update_job, name='job_update'),
    path('api/jobs/<int:job_id>/delete/', api_delete_job, name='job_delete'),
    path('api/jobs/bulk/', api_bulk_jobs, name='job_bulk'),

   # TASK CRUD — function-based views, вложенные в job_id
    path('api/jobs/<int:job_id>/tasks/', api_get_all_tasks, name='job_task_list'),
    path('api/jobs/<int:job_id>/tasks/statistics/', api_get_task_statistics, name='job_task_statistics'),
    path('api/jobs/<int:job_id>/tasks/create/', api_create_task, name='job_task_create'),
    path('api/jobs/<int:job_id>/tasks/<int:task_id>/', api_get_task_detail, name='job_task_detail'),
    path('api/jobs/<int:job_id>/tasks/<int:task_id>/update/', api_update_task, name='job_task_update'),
    path('api/jobs/<int:job_id>/tasks/<int:task_id>/delete/', api_delete_task, name='job_task_delete'),
    # Calendar API
    path('api/calendar/tasks/', api_views.calendar_tasks, name='api_calendar_tasks'),

    # New Job CRUD APIs (DRF)
    path('api/crm/jobs/', api_views.CrmJobListCreateView.as_view(), name='crmjob-list'),
    path('api/crm/jobs/<int:pk>/', api_views.CrmJobDetailView.as_view(), name='crmjob-detail'),

    
]

