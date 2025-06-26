from django.urls import path
from . import api_views
from .api_jwt_email import EmailTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import JobTaskCrudAPIView
from .api_views import all_crm_tasks

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    # JWT Auth
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/email/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair_email'),

    # Job APIs
    path('api/jobs/', api_views.JobListCreateView.as_view(), name='api_job_list'),
    path('api/jobs/<int:pk>/', api_views.JobDetailView.as_view(), name='api_job_detail'),

    # Task APIs
    path('api/tasks/', api_views.TaskListCreateView.as_view(), name='api_task_list'),
    path('api/tasks/<int:pk>/', api_views.TaskDetailView.as_view(), name='api_task_detail'),
    path('api/developer/tasks/', api_views.DeveloperTasksView.as_view(), name='api_developer_tasks'),

    # Dashboard APIs
    path('api/dashboard/stats/', api_views.dashboard_stats, name='api_dashboard_stats'),
    path('api/dashboard/monthly-revenue/', api_views.monthly_revenue_chart, name='api_monthly_revenue'),
    path('api/dashboard/project-distribution/', api_views.project_status_distribution, name='api_project_distribution'),
    path('api/dashboard/recent-projects/', api_views.recent_projects, name='api_recent_projects'),
    path('api/dashboard/upcoming-deadlines/', api_views.upcoming_deadlines, name='api_upcoming_deadlines'),



    # Calendar API
    path('api/calendar/tasks/', api_views.calendar_tasks, name='api_calendar_tasks'),

    # New Job CRUD APIs (DRF)
    path('api/crm/jobs/', api_views.CrmJobListCreateView.as_view(), name='crmjob-list'),
    path('api/crm/jobs/<int:pk>/', api_views.CrmJobDetailView.as_view(), name='crmjob-detail'),
    path('api/crm/jobs/<int:pk>/tasks/', JobTaskCrudAPIView.as_view(), name='crm_job_tasks_crud'),
    path('api/crm/tasks/', all_crm_tasks, name='all_crm_tasks'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)