# user_urls.py
from django.urls import path
from . import user_views

urlpatterns = [
    # User CRUD operations
    path('users/', user_views.UserListCreateAPIView.as_view(), name='user_list_create'),
    path('users/<int:pk>/', user_views.UserRetrieveUpdateDestroyAPIView.as_view(), name='user_detail'),

    # User management actions
    path('users/<int:pk>/change-password/', user_views.change_user_password, name='user_change_password'),
    path('users/<int:pk>/toggle-active/', user_views.toggle_user_active, name='user_toggle_active'),

    # Bulk operations
    path('users/bulk-action/', user_views.bulk_user_action, name='user_bulk_action'),

    # Statistics
    path('users/stats/', user_views.user_stats, name='user_stats'),
]