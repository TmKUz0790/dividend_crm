# # --- Kanban Board ViewSet ---
# from rest_framework.views import APIView
# from .serializers import VaronkaBoardSerializer
# from rest_framework.response import Response
#
# class VaronkaBoardView(APIView):
#     """Endpoint для Kanban board: этапы + заявки по статусам"""
#     def get(self, request):
#         varonkas = Varonka.objects.all()
#         data = VaronkaBoardSerializer(varonkas, many=True).data
#         return Response(data)
# # views.py
# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from .model_sales_funnel import Varonka, VaronkaTask, Application, ApplicationTaskCompletion
# from .serializers import (
#     VaronkaSerializer, VaronkaListSerializer, VaronkaTaskSerializer,
#     ApplicationSerializer, ApplicationListSerializer, ApplicationTaskCompletionSerializer
# )
#
#
# class VaronkaViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for Varonka CRUD operations
#     """
#     queryset = Varonka.objects.all().order_by('-created_at')
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return VaronkaListSerializer
#         return VaronkaSerializer
#
#     @action(detail=True, methods=['post'])
#     def add_task(self, request, pk=None):
#         """Add a new task to this varonka"""
#         varonka = self.get_object()
#         serializer = VaronkaTaskSerializer(data=request.data)
#
#         if serializer.is_valid():
#             serializer.save(varonka=varonka)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['get'])
#     def applications(self, request, pk=None):
#         """Get all applications using this varonka"""
#         varonka = self.get_object()
#         applications = varonka.application_set.all()
#         serializer = ApplicationListSerializer(applications, many=True)
#         return Response(serializer.data)
#
#
# class VaronkaTaskViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for VaronkaTask CRUD operations
#     """
#     queryset = VaronkaTask.objects.all().order_by('varonka', 'order')
#     serializer_class = VaronkaTaskSerializer
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         varonka_id = self.request.query_params.get('varonka', None)
#         if varonka_id is not None:
#             queryset = queryset.filter(varonka_id=varonka_id)
#         return queryset
#
#
# class ApplicationViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for Application CRUD operations
#     """
#     queryset = Application.objects.all().order_by('-created_at')
#
#     def get_serializer_class(self):
#         if self.action == 'list':
#             return ApplicationListSerializer
#         return ApplicationSerializer
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         varonka_id = self.request.query_params.get('varonka', None)
#         status_filter = self.request.query_params.get('status', None)
#
#         if varonka_id is not None:
#             queryset = queryset.filter(varonka_id=varonka_id)
#         if status_filter is not None:
#             queryset = queryset.filter(status=status_filter)
#
#         return queryset
#
#     @action(detail=True, methods=['post'])
#     def complete_task(self, request, pk=None):
#         """Complete a specific task for this application"""
#         application = self.get_object()
#         task_id = request.data.get('task_id')
#
#         if not task_id:
#             return Response({'error': 'task_id is required'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             task = VaronkaTask.objects.get(id=task_id, varonka=application.varonka)
#         except VaronkaTask.DoesNotExist:
#             return Response({'error': 'Task not found or not part of this varonka'},
#                             status=status.HTTP_404_NOT_FOUND)
#
#         # Check if already completed
#         if ApplicationTaskCompletion.objects.filter(
#                 application=application, varonka_task=task
#         ).exists():
#             return Response({'error': 'Task already completed'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         # Create completion record
#         completion_data = {
#             'application': application.id,
#             'varonka_task': task.id,
#             'notes': request.data.get('notes', ''),
#             'completed_by': request.data.get('completed_by', '')
#         }
#
#         serializer = ApplicationTaskCompletionSerializer(data=completion_data)
#         if serializer.is_valid():
#             serializer.save()
#
#             # Update application status if all required tasks are done
#             if application.is_completed():
#                 application.status = 'completed'
#                 application.save()
#
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['delete'])
#     def uncomplete_task(self, request, pk=None):
#         """Remove completion for a specific task"""
#         application = self.get_object()
#         task_id = request.query_params.get('task_id')
#
#         if not task_id:
#             return Response({'error': 'task_id is required'},
#                             status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             completion = ApplicationTaskCompletion.objects.get(
#                 application=application,
#                 varonka_task_id=task_id
#             )
#             completion.delete()
#
#             # Update application status
#             if application.status == 'completed':
#                 application.status = 'active'
#                 application.save()
#
#             return Response({'message': 'Task completion removed'},
#                             status=status.HTTP_204_NO_CONTENT)
#
#         except ApplicationTaskCompletion.DoesNotExist:
#             return Response({'error': 'Task completion not found'},
#                             status=status.HTTP_404_NOT_FOUND)
#
#     @action(detail=True, methods=['get'])
#     def tasks(self, request, pk=None):
#         """Get all varonka tasks for this application with completion status"""
#         application = self.get_object()
#         varonka_tasks = application.get_varonka_tasks()
#         completed_task_ids = application.task_completions.values_list('varonka_task_id', flat=True)
#
#         tasks_data = []
#         for task in varonka_tasks:
#             task_data = VaronkaTaskSerializer(task).data
#             task_data['is_completed'] = task.id in completed_task_ids
#             tasks_data.append(task_data)
#
#         return Response(tasks_data)
#
#
# class ApplicationTaskCompletionViewSet(viewsets.ModelViewSet):
#     """
#     ViewSet for ApplicationTaskCompletion CRUD operations
#     """
#     queryset = ApplicationTaskCompletion.objects.all().order_by('-completed_at')
#     serializer_class = ApplicationTaskCompletionSerializer
#
#     def get_queryset(self):
#         queryset = super().get_queryset()
#         application_id = self.request.query_params.get('application', None)
#
#         if application_id is not None:
#             queryset = queryset.filter(application_id=application_id)
#
#         return queryset


from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .model_sales_funnel import (
    Varonka, VaronkaStage, VaronkaTask, Application,
    ApplicationTaskCompletion, VaronkaTemplate
)
from .varanka_serializers import (
    VaronkaSerializer, VaronkaListSerializer, VaronkaStageSerializer,
    VaronkaTaskSerializer, ApplicationSerializer, ApplicationListSerializer,
    ApplicationTaskCompletionSerializer, VaronkaBoardSerializer
)


class VaronkaBoardView(APIView):
    """Endpoint для Kanban board: этапы + заявки по статусам"""

    def get(self, request):
        varonka_id = request.query_params.get('varonka')
        if not varonka_id:
            return Response({'error': 'varonka parameter is required'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            varonka = Varonka.objects.get(id=varonka_id)
        except Varonka.DoesNotExist:
            return Response({'error': 'Varonka not found'},
                            status=status.HTTP_404_NOT_FOUND)

        # Get all stages for this varonka with their applications
        stages_data = []
        for stage in varonka.stages.all().order_by('order'):
            applications = Application.objects.filter(
                varonka=varonka,
                current_stage=stage
            ).order_by('-created_at')

            stage_data = {
                'id': stage.id,
                'name': stage.name,
                'slug': stage.slug,
                'color': stage.color,
                'applications': ApplicationListSerializer(applications, many=True).data
            }
            stages_data.append(stage_data)

        return Response({
            'varonka': VaronkaSerializer(varonka).data,
            'stages': stages_data
        })


class VaronkaViewSet(viewsets.ModelViewSet):
    """ViewSet for Varonka CRUD operations"""
    queryset = Varonka.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return VaronkaListSerializer
        return VaronkaSerializer

    @action(detail=True, methods=['get'])
    def stages(self, request, pk=None):
        """Get all stages for this varonka"""
        varonka = self.get_object()
        stages = varonka.stages.all().order_by('order')
        serializer = VaronkaStageSerializer(stages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_stage(self, request, pk=None):
        """Add a new stage to this varonka"""
        varonka = self.get_object()
        data = request.data.copy()
        data['varonka'] = varonka.id

        serializer = VaronkaStageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_task(self, request, pk=None):
        """Add a new task to this varonka"""
        varonka = self.get_object()
        data = request.data.copy()
        data['varonka'] = varonka.id

        serializer = VaronkaTaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def applications(self, request, pk=None):
        """Get all applications using this varonka"""
        varonka = self.get_object()
        applications = varonka.application_set.all().order_by('-created_at')
        serializer = ApplicationListSerializer(applications, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def create_from_template(self, request, pk=None):
        """Create varonka from template"""
        template_id = request.data.get('template_id')
        varonka_name = request.data.get('name')

        if not template_id or not varonka_name:
            return Response(
                {'error': 'template_id and name are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            template = VaronkaTemplate.objects.get(id=template_id)
            varonka = template.create_varonka(varonka_name)
            serializer = VaronkaSerializer(varonka)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except VaronkaTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class VaronkaStageViewSet(viewsets.ModelViewSet):
    """ViewSet for VaronkaStage CRUD operations"""
    queryset = VaronkaStage.objects.all().order_by('varonka', 'order')
    serializer_class = VaronkaStageSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        varonka_id = self.request.query_params.get('varonka')
        if varonka_id:
            queryset = queryset.filter(varonka_id=varonka_id)
        return queryset


class VaronkaTaskViewSet(viewsets.ModelViewSet):
    """ViewSet for VaronkaTask CRUD operations"""
    queryset = VaronkaTask.objects.all().order_by('varonka', 'order')
    serializer_class = VaronkaTaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        varonka_id = self.request.query_params.get('varonka')
        if varonka_id:
            queryset = queryset.filter(varonka_id=varonka_id)
        return queryset


class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet for Application CRUD operations"""
    queryset = Application.objects.all().order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return ApplicationListSerializer
        return ApplicationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        varonka_id = self.request.query_params.get('varonka')
        stage_id = self.request.query_params.get('stage')
        status_filter = self.request.query_params.get('status')  # backward compatibility

        if varonka_id:
            queryset = queryset.filter(varonka_id=varonka_id)
        if stage_id:
            queryset = queryset.filter(current_stage_id=stage_id)
        if status_filter:
            # Backward compatibility: filter by stage slug
            queryset = queryset.filter(current_stage__slug=status_filter)

        return queryset

    @action(detail=True, methods=['post'])
    def move_to_stage(self, request, pk=None):
        """Move application to a different stage"""
        application = self.get_object()
        stage_id = request.data.get('stage_id')

        if not stage_id:
            return Response(
                {'error': 'stage_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            target_stage = VaronkaStage.objects.get(
                id=stage_id,
                varonka=application.varonka
            )
        except VaronkaStage.DoesNotExist:
            return Response(
                {'error': 'Stage not found or not part of this varonka'},
                status=status.HTTP_404_NOT_FOUND
            )

        if application.move_to_stage(target_stage):
            serializer = ApplicationSerializer(application)
            return Response(serializer.data)
        else:
            return Response(
                {'error': 'Cannot move to this stage. Required tasks not completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        """Complete a specific task for this application"""
        application = self.get_object()
        task_id = request.data.get('task_id')

        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            task = VaronkaTask.objects.get(
                id=task_id,
                varonka=application.varonka
            )
        except VaronkaTask.DoesNotExist:
            return Response(
                {'error': 'Task not found or not part of this varonka'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if already completed
        if ApplicationTaskCompletion.objects.filter(
                application=application,
                varonka_task=task
        ).exists():
            return Response(
                {'error': 'Task already completed'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create completion record
        completion_data = {
            'application': application.id,
            'varonka_task': task.id,
            'notes': request.data.get('notes', ''),
            'completed_by': request.data.get('completed_by', '')
        }

        serializer = ApplicationTaskCompletionSerializer(data=completion_data)
        if serializer.is_valid():
            completion = serializer.save()

            # Auto-move to next stage if task completion allows it
            if task.required_for_stage:
                if application.can_move_to_stage(task.required_for_stage):
                    application.move_to_stage(task.required_for_stage)

            # Update to final stage if all required tasks are done
            elif application.is_completed():
                final_stage = application.varonka.stages.filter(is_final=True).first()
                if final_stage:
                    application.move_to_stage(final_stage)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def uncomplete_task(self, request, pk=None):
        """Remove completion for a specific task"""
        application = self.get_object()
        task_id = request.query_params.get('task_id')

        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            completion = ApplicationTaskCompletion.objects.get(
                application=application,
                varonka_task_id=task_id
            )
            completion.delete()

            # Optionally move back to previous stage
            # This logic can be customized based on your business rules
            current_stage_order = application.current_stage.order
            if current_stage_order > 0:
                prev_stage = application.varonka.stages.filter(
                    order__lt=current_stage_order
                ).order_by('-order').first()
                if prev_stage:
                    application.move_to_stage(prev_stage)

            return Response(
                {'message': 'Task completion removed'},
                status=status.HTTP_204_NO_CONTENT
            )

        except ApplicationTaskCompletion.DoesNotExist:
            return Response(
                {'error': 'Task completion not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """Get all varonka tasks for this application with completion status"""
        application = self.get_object()
        varonka_tasks = application.get_varonka_tasks()
        completed_task_ids = application.task_completions.values_list(
            'varonka_task_id', flat=True
        )

        tasks_data = []
        for task in varonka_tasks:
            task_data = VaronkaTaskSerializer(task).data
            task_data['is_completed'] = task.id in completed_task_ids

            # Add completion details if completed
            if task.id in completed_task_ids:
                completion = application.task_completions.get(varonka_task=task)
                task_data['completion'] = ApplicationTaskCompletionSerializer(completion).data

            tasks_data.append(task_data)

        return Response(tasks_data)


class ApplicationTaskCompletionViewSet(viewsets.ModelViewSet):
    """ViewSet for ApplicationTaskCompletion CRUD operations"""
    queryset = ApplicationTaskCompletion.objects.all().order_by('-completed_at')
    serializer_class = ApplicationTaskCompletionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        application_id = self.request.query_params.get('application')

        if application_id:
            queryset = queryset.filter(application_id=application_id)

        return queryset