from rest_framework.routers import DefaultRouter
from .views_kanban import StageViewSet, ClientViewSet, KanbanTaskViewSet, KanbanBoardViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'stages', StageViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'tasks', KanbanTaskViewSet)

kanban_board = KanbanBoardViewSet.as_view({'get': 'board'})
kanban_stats = KanbanBoardViewSet.as_view({'get': 'stats'})

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/kanban/board/', kanban_board, name='kanban-board'),
    path('api/kanban/stats/', kanban_stats, name='kanban-stats'),
]
