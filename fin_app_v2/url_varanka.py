# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .sales_funnel_views import (
    VaronkaBoardView, VaronkaViewSet, 
    VaronkaTaskViewSet, ApplicationViewSet, ApplicationTaskCompletionViewSet
)

router = DefaultRouter()
router.register(r'varonkas', VaronkaViewSet)
router.register(r'varonka-tasks', VaronkaTaskViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'task-completions', ApplicationTaskCompletionViewSet)

urlpatterns = [
    # Kanban board endpoint
    path('kanban-board-varanka/', VaronkaBoardView.as_view(), name='kanban-board'),

    # Include router URLs
    path('api-varanka/', include(router.urls)),
]
