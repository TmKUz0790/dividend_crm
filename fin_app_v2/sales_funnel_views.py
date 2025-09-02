# --- Kanban Board ViewSet ---
from rest_framework.views import APIView
from .serializers import VaronkaBoardSerializer
from rest_framework.response import Response

class VaronkaBoardView(APIView):
    """Endpoint для Kanban board: этапы + заявки по статусам"""
    def get(self, request):
        varonkas = Varonka.objects.all()
        data = VaronkaBoardSerializer(varonkas, many=True).data
        return Response(data)
# views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .model_sales_funnel import Varonka, VaronkaTask, Application, ApplicationTaskCompletion
from .serializers import (
    VaronkaSerializer, VaronkaListSerializer, VaronkaTaskSerializer,
    ApplicationSerializer, ApplicationListSerializer, ApplicationTaskCompletionSerializer
)


class VaronkaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Varonka CRUD operations
    """
    queryset = Varonka.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return VaronkaListSerializer
        return VaronkaSerializer

    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Add a new task to this varonka"""
        varonka = self.get_object()
        serializer = VaronkaTaskSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(varonka=varonka)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get all applications using this varonka"""
        varonka = self.get_object()
        applications = varonka.application_set.all()
        serializer = ApplicationListSerializer(applications, many=True)
        return Response(serializer.data)


class VaronkaTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for VaronkaTask CRUD operations
    """
    queryset = VaronkaTask.objects.all().order_by('varonka', 'order')
    serializer_class = VaronkaTaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        varonka_id = self.request.query_params.get('varonka', None)
        if varonka_id is not None:
            queryset = queryset.filter(varonka_id=varonka_id)
        return queryset


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Application CRUD operations
    """
    queryset = Application.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        return ApplicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        varonka_id = self.request.query_params.get('varonka', None)
        status_filter = self.request.query_params.get('status', None)

        if varonka_id is not None:
            queryset = queryset.filter(varonka_id=varonka_id)
        if status_filter is not None:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """Complete a specific task for this application"""
        application = self.get_object()
        task_id = request.data.get('task_id')

        if not task_id:
            return Response({'error': 'task_id is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            task = VaronkaTask.objects.get(id=task_id, varonka=application.varonka)
        except VaronkaTask.DoesNotExist:
            return Response({'error': 'Task not found or not part of this varonka'},
                            status=status.HTTP_404_NOT_FOUND)

        # Check if already completed

        if ApplicationTaskCompletion.objects.filter(
            application=application, varonka=application.varonka
        ).exists():
            return Response({'error': 'Task already completed'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Create completion record
        completion_data = {
            'application': application.id,
            'varonka': application.varonka.id,
            'notes': request.data.get('notes', ''),
            'completed_by': request.data.get('completed_by', '')
        }

        serializer = ApplicationTaskCompletionSerializer(data=completion_data)
        if serializer.is_valid():
            serializer.save()

            # Update application status if all required tasks are done
            if hasattr(application, 'is_completed') and application.is_completed():
                application.status = 'completed'
                application.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def uncomplete_task(self, request, pk=None):
        """Remove completion for a specific task"""
        application = self.get_object()
        task_id = request.query_params.get('task_id')

        if not task_id:
            return Response({'error': 'task_id is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            completion = ApplicationTaskCompletion.objects.get(
                application=application,
                varonka=application.varonka
            )
            completion.delete()

            # Update application status
            if application.status == 'completed':
                application.status = 'active'
                application.save()

            return Response({'message': 'Task completion removed'},
                            status=status.HTTP_204_NO_CONTENT)

        except ApplicationTaskCompletion.DoesNotExist:
            return Response({'error': 'Task completion not found'},
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all varonka tasks for this application with completion status"""
        application = self.get_object()
        varonka_tasks = application.get_varonka_tasks()
        completed_varonka_ids = application.task_completions.values_list('varonka_id', flat=True)

        tasks_data = []
        for task in varonka_tasks:
            task_data = VaronkaTaskSerializer(task).data
            task_data['is_completed'] = application.varonka.id in completed_varonka_ids
            tasks_data.append(task_data)

        return Response(tasks_data)


class ApplicationTaskCompletionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ApplicationTaskCompletion CRUD operations
    """
    queryset = ApplicationTaskCompletion.objects.all().order_by('-completed_at')
    serializer_class = ApplicationTaskCompletionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        application_id = self.request.query_params.get('application', None)

        if application_id is not None:
            queryset = queryset.filter(application_id=application_id)

        return queryset