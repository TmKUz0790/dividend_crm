from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .model_sales_funnel import Application, Varonka, VaronkaTask, ApplicationTaskCompletion, VaronkaTemplate, \
    VaronkaTemplateTask
from .serializers import (
    ApplicationSerializer,
    VaronkaSerializer,
    VaronkaTaskSerializer,
    ApplicationTaskCompletionSerializer,
    VaronkaTemplateSerializer,
    VaronkaTemplateTaskSerializer
)


# Application CRUD
class ApplicationListCreateAPIView(generics.ListCreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class ApplicationRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


# Varonka CRUD
class VaronkaListCreateAPIView(generics.ListCreateAPIView):
    queryset = Varonka.objects.all()
    serializer_class = VaronkaSerializer


class VaronkaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Varonka.objects.all()
    serializer_class = VaronkaSerializer


# VaronkaTask CRUD
class VaronkaTaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = VaronkaTask.objects.all()
    serializer_class = VaronkaTaskSerializer

    def get_queryset(self):
        """Filter tasks by varonka if varonka_id is provided in URL"""
        queryset = VaronkaTask.objects.all()
        varonka_id = self.request.query_params.get('varonka_id')
        if varonka_id:
            queryset = queryset.filter(varonka_id=varonka_id)
        return queryset.order_by('order')


class VaronkaTaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaronkaTask.objects.all()
    serializer_class = VaronkaTaskSerializer


# ApplicationTaskCompletion CRUD
class ApplicationTaskCompletionListCreateAPIView(generics.ListCreateAPIView):
    queryset = ApplicationTaskCompletion.objects.all()
    serializer_class = ApplicationTaskCompletionSerializer

    def get_queryset(self):
        """Filter completions by application if application_id is provided"""
        queryset = ApplicationTaskCompletion.objects.all()
        application_id = self.request.query_params.get('application_id')
        if application_id:
            queryset = queryset.filter(application_id=application_id)
        return queryset


class ApplicationTaskCompletionRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ApplicationTaskCompletion.objects.all()
    serializer_class = ApplicationTaskCompletionSerializer


# VaronkaTemplate CRUD
class VaronkaTemplateListCreateAPIView(generics.ListCreateAPIView):
    queryset = VaronkaTemplate.objects.all()
    serializer_class = VaronkaTemplateSerializer


class VaronkaTemplateRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaronkaTemplate.objects.all()
    serializer_class = VaronkaTemplateSerializer


# VaronkaTemplateTask CRUD
class VaronkaTemplateTaskListCreateAPIView(generics.ListCreateAPIView):
    queryset = VaronkaTemplateTask.objects.all()
    serializer_class = VaronkaTemplateTaskSerializer

    def get_queryset(self):
        """Filter template tasks by template if template_id is provided"""
        queryset = VaronkaTemplateTask.objects.all()
        template_id = self.request.query_params.get('template_id')
        if template_id:
            queryset = queryset.filter(template_id=template_id)
        return queryset.order_by('order')


class VaronkaTemplateTaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VaronkaTemplateTask.objects.all()
    serializer_class = VaronkaTemplateTaskSerializer


# Custom API endpoints for business logic
@api_view(['POST'])
def complete_task(request):
    """Mark a task as completed for an application"""
    application_id = request.data.get('application_id')
    task_id = request.data.get('task_id')
    notes = request.data.get('notes', '')
    completed_by = request.data.get('completed_by', '')

    try:
        application = Application.objects.get(id=application_id)
        task = VaronkaTask.objects.get(id=task_id)

        # Check if task belongs to application's varonka
        if task.varonka != application.varonka:
            return Response(
                {'error': 'Task does not belong to application\'s varonka'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create or update completion
        completion, created = ApplicationTaskCompletion.objects.get_or_create(
            application=application,
            task=task,
            defaults={
                'notes': notes,
                'completed_by': completed_by
            }
        )

        if not created:
            completion.notes = notes
            completion.completed_by = completed_by
            completion.save()

        # Update application's current task to next task
        next_task = application.get_next_task()
        application.current_task = next_task

        # Update stage based on progress
        if next_task is None:  # All tasks completed
            application.stage = 'done'
            application.is_done = True
        elif application.stage == 'new':
            application.stage = 'in_progress'

        application.save()

        serializer = ApplicationTaskCompletionSerializer(completion)
        return Response({
            'completion': serializer.data,
            'next_task_id': next_task.id if next_task else None,
            'progress_percentage': application.progress_percentage()
        })

    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    except VaronkaTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def application_progress(request, application_id):
    """Get application progress and next tasks"""
    try:
        application = Application.objects.get(id=application_id)
        next_task = application.get_next_task()
        completed_tasks = application.task_completions.all()

        return Response({
            'application_id': application.id,
            'application_name': application.name,
            'varonka_name': application.varonka.name if application.varonka else None,
            'current_task': {
                'id': application.current_task.id,
                'name': application.current_task.name
            } if application.current_task else None,
            'next_task': {
                'id': next_task.id,
                'name': next_task.name,
                'description': next_task.description
            } if next_task else None,
            'progress_percentage': application.progress_percentage(),
            'completed_tasks_count': completed_tasks.count(),
            'total_tasks_count': application.varonka.tasks.count() if application.varonka else 0,
            'stage': application.stage,
            'is_done': application.is_done
        })

    except Application.DoesNotExist:
        return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def create_varonka_from_template(request):
    """Create a new varonka from a template"""
    template_id = request.data.get('template_id')
    varonka_name = request.data.get('varonka_name')

    if not template_id or not varonka_name:
        return Response(
            {'error': 'template_id and varonka_name are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        template = VaronkaTemplate.objects.get(id=template_id)
        varonka = template.create_varonka(varonka_name)

        serializer = VaronkaSerializer(varonka)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except VaronkaTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def varonka_with_tasks(request, varonka_id):
    """Get varonka with all its tasks"""
    try:
        varonka = Varonka.objects.get(id=varonka_id)
        tasks = varonka.tasks.all().order_by('order')

        varonka_data = VaronkaSerializer(varonka).data
        tasks_data = VaronkaTaskSerializer(tasks, many=True).data

        return Response({
            'varonka': varonka_data,
            'tasks': tasks_data
        })

    except Varonka.DoesNotExist:
        return Response({'error': 'Varonka not found'}, status=status.HTTP_404_NOT_FOUND)