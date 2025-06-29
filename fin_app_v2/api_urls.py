# from django.urls import path
# from . import api_views
# from .api_jwt_email import EmailTokenObtainPairView
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from .api_views import JobTaskCrudAPIView
# from .api_views import all_crm_tasks
#
# from django.conf import settings
# from django.conf.urls.static import static
# urlpatterns = [
#     # JWT Auth
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     path('api/token/email/', EmailTokenObtainPairView.as_view(), name='token_obtain_pair_email'),
#
#     # Job APIs
#     path('api/jobs/', api_views.JobListCreateView.as_view(), name='api_job_list'),
#     path('api/jobs/<int:pk>/', api_views.JobDetailView.as_view(), name='api_job_detail'),
#
#     # Task APIs
#     path('api/tasks/', api_views.TaskListCreateView.as_view(), name='api_task_list'),
#     path('api/tasks/<int:pk>/', api_views.TaskDetailView.as_view(), name='api_task_detail'),
#     path('api/developer/tasks/', api_views.DeveloperTasksView.as_view(), name='api_developer_tasks'),
#
#     # Dashboard APIs
#     path('api/dashboard/stats/', api_views.dashboard_stats, name='api_dashboard_stats'),
#     path('api/dashboard/monthly-revenue/', api_views.monthly_revenue_chart, name='api_monthly_revenue'),
#     path('api/dashboard/project-distribution/', api_views.project_status_distribution, name='api_project_distribution'),
#     path('api/dashboard/recent-projects/', api_views.recent_projects, name='api_recent_projects'),
#     path('api/dashboard/upcoming-deadlines/', api_views.upcoming_deadlines, name='api_upcoming_deadlines'),
#
#
#
#     # Calendar API
#     path('api/calendar/tasks/', api_views.calendar_tasks, name='api_calendar_tasks'),
#
#     # New Job CRUD APIs (DRF)
#     #path('api/crm/jobs/', api_views.CrmJobListCreateView.as_view(), name='crmjob-list'),
#     path('api/crm/jobs/<int:pk>/', api_views.CrmJobDetailView.as_view(), name='crmjob-detail'),
#     path('api/crm/jobs/<int:pk>/tasks/', api_views.JobTaskCrudAPIView.as_view(), name='crm_job_tasks_crud'),
#     path('api/crm/tasks/', all_crm_tasks, name='all_crm_tasks'),
#
#
#
#     # New bitch
#
#     # ADD THESE TO YOUR urls.py
#     path('api/existing-jobs/', api_views.get_existing_jobs, name='get_existing_jobs'),
#     path('api/job-details/', api_views.get_job_details, name='get_job_details'),
#     path('api/company-suggestions/', api_views.get_company_suggestions, name='get_company_suggestions'),
#     path('crm/create/', api_views.crm_form_view, name='crm_create'),
# ]
#
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


from django.urls import path
from . import api_views
from .api_jwt_email import EmailTokenObtainPairView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .api_views import UserListView, all_crm_tasks
from . import user_views

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

    # CRM Job Management
    path('api/crm/jobs/', api_views.CrmJobListCreateView.as_view(), name='crm-all-views'),
    path('api/crm/jobs/<int:pk>/', api_views.CrmJobDetailView.as_view(), name='crmjob-detail'),
    path('api/crm/jobs/<int:pk>/tasks/', api_views.JobTaskCrudAPIView.as_view(), name='crm_job_tasks_crud'),
    path('api/crm/tasks/', all_crm_tasks, name='all_crm_tasks'),

    # Individual File Management APIs (NEW - 100MB Support)
    path('api/tasks/<int:task_id>/files/', api_views.get_task_files, name='get_task_files'),
    path('api/tasks/<int:task_id>/files/add/', api_views.add_files_to_task, name='add_files_to_task'),
    path('api/tasks/<int:task_id>/files/<int:file_id>/delete/', api_views.delete_file_from_task,
         name='delete_file_from_task'),
    path('api/tasks/<int:task_id>/files/<int:file_id>/download/', api_views.download_file, name='download_file'),
    path('api/tasks/<int:task_id>/files/bulk-delete/', api_views.bulk_delete_files, name='bulk_delete_files'),

    # Helper endpoints for CRM form
    path('api/existing-jobs/', api_views.get_existing_jobs, name='get_existing_jobs'),
    path('api/job-details/', api_views.get_job_details, name='get_job_details'),
    path('api/company-suggestions/', api_views.get_company_suggestions, name='get_company_suggestions'),

    # Storage and utilities
    path('api/storage-stats/', api_views.get_storage_stats, name='get_storage_stats'),

    # CRM Form View
    path('crm/create/', api_views.crm_form_view, name='crm_create'),


    path('api/users/', UserListView.as_view(), name='user-list'),


    # Authentication
    path('auth/token/', user_views.CustomAuthToken.as_view(), name='auth_token'),
    path('auth/login/', user_views.login_view, name='auth_login'),
    path('auth/logout/', user_views.logout_view, name='auth_logout'),
    path('auth/check/', user_views.check_auth, name='auth_check'),

    # User CRUD
    path('users/', user_views.UserListCreateAPIView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', user_views.UserRetrieveUpdateDestroyAPIView.as_view(), name='user_detail'),
    path('users/<int:pk>/change-password/', user_views.change_user_password, name='user_change_password'),
    path('users/<int:pk>/toggle-active/', user_views.toggle_user_active, name='user_toggle_active'),
    path('users/bulk-action/', user_views.bulk_user_action, name='user_bulk_action'),
    path('users/stats/', user_views.user_stats, name='user_stats'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



    """



Endpoints:
POST /api/auth/token/ - Get token
POST /api/auth/login/ - Session login
POST /api/auth/logout/ - Logout
GET /api/auth/check/ - Check auth

GET /api/users/ - List users
POST /api/users/ - Create user
GET /api/users/{id}/ - User detail
PUT/PATCH /api/users/{id}/ - Update user
DELETE /api/users/{id}/ - Delete user
POST /api/users/{id}/change-password/ - Change password
POST /api/users/{id}/toggle-active/ - Toggle active
POST /api/users/bulk-action/ - Bulk actions
GET /api/users/stats/ - Statistics
"""