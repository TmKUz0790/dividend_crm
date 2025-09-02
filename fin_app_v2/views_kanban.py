from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models_kanban import Stage, Client, KanbanTask
from .serializers_kanban import StageSerializer, ClientSerializer, KanbanTaskSerializer

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all().order_by('order')
    serializer_class = StageSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

class KanbanTaskViewSet(viewsets.ModelViewSet):
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        task = self.get_object()
        new_status = request.data.get('status')
        if new_status not in dict(KanbanTask.STATUS_CHOICES):
            return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
        task.status = new_status
        task.save()
        return Response({'id': task.id, 'status': task.status})
    queryset = KanbanTask.objects.all().order_by('-created_at')
    serializer_class = KanbanTaskSerializer

class KanbanBoardViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['get'])
    def board(self, request):
        stages = Stage.objects.all().order_by('order')
        result = []
        for stage in stages:
            clients = stage.clients.all()
            tasks_by_status = {'new': [], 'in_progress': [], 'done': []}
            for client in clients:
                for task in client.kanban_tasks.all():
                    tasks_by_status[task.status].append({
                        'id': task.id,
                        'title': task.title,
                        'description': task.description,
                        'status': task.status,
                        'client_id': client.id,
                        'client_name': client.name,
                        'stage_id': stage.id,
                        'stage_name': stage.name,
                        'created_at': task.created_at
                    })
            result.append({
                'stage_id': stage.id,
                'stage_name': stage.name,
                'tasks': tasks_by_status
            })
        return Response(result)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_stages = Stage.objects.count()
        total_clients = Client.objects.count()
        total_tasks = KanbanTask.objects.count()
        tasks_by_status = {
            'new': KanbanTask.objects.filter(status='new').count(),
            'in_progress': KanbanTask.objects.filter(status='in_progress').count(),
            'done': KanbanTask.objects.filter(status='done').count(),
        }
        return Response({
            'total_stages': total_stages,
            'total_clients': total_clients,
            'total_tasks': total_tasks,
            'tasks_by_status': tasks_by_status
        })
