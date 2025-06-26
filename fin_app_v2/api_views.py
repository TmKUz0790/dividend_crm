# api_views.py - CREATE THIS AS A NEW FILE
# This file doesn't exist in your project, so it's 100% safe to add

from django.http import JsonResponse
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import Job, Task, DeductionLog, calculate_income_balance
from .serializers import (
    JobSerializer, TaskSerializer, UserSerializer,
    DeductionLogSerializer, DashboardStatsSerializer
)
from rest_framework import viewsets
from .models_crm import CrmJob, CrmTask, CrmTaskComment, CrmTaskFile
from .serializers import CrmJobSerializer, CrmTaskSerializer, CrmTaskCommentSerializer, CrmTaskFileSerializer


class IsAdminUser(permissions.BasePermission):
    """Custom permission to only allow admin users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.email == 'Admin@dbr.org'


# Job API Views
class JobListCreateView(generics.ListCreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Job.objects.all()
        # Filter by status if provided
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'completed':
            # Jobs with all tasks completed
            queryset = queryset.filter(tasks__progress=100).distinct()
        elif status_filter == 'in_progress':
            # Jobs with at least one task in progress
            queryset = queryset.filter(tasks__progress__gt=0, tasks__progress__lt=100).distinct()
        elif status_filter == 'overdue':
            # Jobs with overdue tasks
            today = timezone.now().date()
            queryset = queryset.filter(tasks__deadline__lt=today, tasks__progress__lt=100).distinct()

        return queryset.order_by('-created_at')


class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.AllowAny]

    def destroy(self, request, *args, **kwargs):
        # Only admin can delete jobs
        if request.user.email != 'Admin@dbr.org':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)


# Task API Views
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Task.objects.select_related('job').prefetch_related('assigned_users')

        # Filter by job if provided
        job_id = self.request.query_params.get('job', None)
        if job_id:
            queryset = queryset.filter(job_id=job_id)

        # Filter by assigned user
        user_id = self.request.query_params.get('user', None)
        if user_id:
            queryset = queryset.filter(assigned_users__id=user_id)

        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'completed':
            queryset = queryset.filter(progress=100)
        elif status_filter == 'in_progress':
            queryset = queryset.filter(progress__gt=0, progress__lt=100)
        elif status_filter == 'pending':
            queryset = queryset.filter(progress=0)
        elif status_filter == 'overdue':
            today = timezone.now().date()
            queryset = queryset.filter(deadline__lt=today, progress__lt=100)

        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(deadline__gte=date_from)
        if date_to:
            queryset = queryset.filter(deadline__lte=date_to)

        return queryset.order_by('deadline')


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]

    def update(self, request, *args, **kwargs):
        # Check if user can update this task
        task = self.get_object()
        if (request.user not in task.assigned_users.all() and
                request.user.email != 'Admin@dbr.org'):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)


# Developer Task Views
class DeveloperTasksView(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Task.objects.filter(
            assigned_users=self.request.user
        ).select_related('job').order_by('deadline')


# Dashboard API Views
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def dashboard_stats(request):
    """Get dashboard statistics"""
    today = timezone.now().date()
    current_month = today.month
    current_year = today.year

    # Basic project stats
    total_projects = Job.objects.count()

    # Project status counts
    in_progress_projects = Job.objects.filter(
        tasks__progress__gt=0, tasks__progress__lt=100
    ).distinct().count()

    completed_projects = Job.objects.filter(
        tasks__progress=100
    ).distinct().count()

    overdue_projects = Job.objects.filter(
        tasks__deadline__lt=today, tasks__progress__lt=100
    ).distinct().count()

    # Financial data
    total_revenue = Job.objects.aggregate(
        total=Sum('over_all_income')
    )['total'] or 0

    monthly_income = Job.objects.filter(
        created_at__year=current_year,
        created_at__month=current_month
    ).aggregate(total=Sum('over_all_income'))['total'] or 0

    # Get income balance
    balance_data = calculate_income_balance()
    income_balance = balance_data['income_balance']

    # Task and user counts
    total_customers = User.objects.count()
    total_transactions = Task.objects.filter(paid=True).count()
    total_products = Task.objects.count()

    stats = {
        'total_projects': total_projects,
        'in_progress_projects': in_progress_projects,
        'completed_projects': completed_projects,
        'overdue_projects': overdue_projects,
        'total_revenue': total_revenue,
        'total_customers': total_customers,
        'total_transactions': total_transactions,
        'total_products': total_products,
        'monthly_income': monthly_income,
        'income_balance': income_balance,
    }

    serializer = DashboardStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def monthly_revenue_chart(request):
    """Get monthly revenue data for charts"""
    from datetime import datetime
    import calendar

    # Get current year or specified year
    year = int(request.query_params.get('year', timezone.now().year))

    monthly_data = []
    for month in range(1, 13):
        # Get jobs created in this month
        jobs_income = Job.objects.filter(
            created_at__year=year,
            created_at__month=month
        ).aggregate(Sum('over_all_income'))['over_all_income__sum'] or 0

        # Get expenses (money paid to developers)
        expenses = Task.objects.filter(
            job__created_at__year=year,
            job__created_at__month=month,
            paid=True
        ).aggregate(Sum('money_for_task'))['money_for_task__sum'] or 0

        profit = jobs_income - expenses

        monthly_data.append({
            'month': calendar.month_abbr[month],
            'income': jobs_income,
            'expenses': expenses,
            'profit': profit
        })

    return Response(monthly_data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def project_status_distribution(request):
    """Get project status distribution for pie chart"""
    today = timezone.now().date()

    # Count projects by status
    in_progress = Job.objects.filter(
        tasks__progress__gt=0, tasks__progress__lt=100
    ).distinct().count()

    completed = Job.objects.filter(
        tasks__progress=100
    ).distinct().count()

    overdue = Job.objects.filter(
        tasks__deadline__lt=today, tasks__progress__lt=100
    ).distinct().count()

    data = [
        {'status': 'В ходе выполнения', 'count': in_progress, 'percentage': 58.33},
        {'status': 'Законченный', 'count': completed, 'percentage': 25},
        {'status': 'Незаконченный', 'count': overdue, 'percentage': 8}
    ]

    return Response(data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def recent_projects(request):
    """Get recent projects for dashboard"""
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    serializer = JobSerializer(recent_jobs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def upcoming_deadlines(request):
    """Get upcoming task deadlines"""
    today = timezone.now().date()
    upcoming_tasks = Task.objects.filter(
        progress__lt=100,
        deadline__gte=today
    ).select_related('job').order_by('deadline')[:10]

    serializer = TaskSerializer(upcoming_tasks, many=True)
    return Response(serializer.data)


# Calendar API Views
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def calendar_tasks(request):
    """Get tasks for calendar view"""
    year = int(request.query_params.get('year', timezone.now().year))
    month = int(request.query_params.get('month', timezone.now().month))

    # Get tasks for the specified month
    tasks = Task.objects.filter(
        deadline__year=year,
        deadline__month=month
    ).select_related('job')

    # Group tasks by date
    tasks_by_date = {}
    for task in tasks:
        date_key = task.deadline.strftime('%Y-%m-%d')
        if date_key not in tasks_by_date:
            tasks_by_date[date_key] = []
        tasks_by_date[date_key].append({
            'id': task.id,
            'title': task.title,
            'progress': task.progress,
            'job_title': task.job.title,
            'status_color': TaskSerializer().get_status_color(task)
        })

    return Response(tasks_by_date)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from django.shortcuts import get_object_or_404
from .models import CrmJob, CrmTask, CrmTaskFile, CrmTaskComment
from .serializers import CrmTaskSerializer, CrmTaskFileSerializer, CrmTaskCommentSerializer
import json


class JobTaskCrudAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser]

    def get(self, request, pk):
        tasks = CrmTask.objects.filter(job_id=pk).order_by('-id')
        serializer = CrmTaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        data = request.data.copy()
        subtasks = json.loads(data.get('subtasks', '[]'))
        files = request.FILES.getlist('files')

        task = CrmTask.objects.create(
            job_id=pk,
            title=data.get('title', ''),
            description=data.get('description', ''),
            task_type=data.get('task_type', 'SIMPLE'),
            assigned_to=data.get('assigned_to', ''),
            subtasks=subtasks
        )

        if comment_text := data.get('comment'):
            CrmTaskComment.objects.create(task=task, author='newcomp@gmail.com', text=comment_text)

        for file in files:
            CrmTaskFile.objects.create(task=task, file=file)

        return Response({'success': True, 'id': task.id}, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        data = request.data.copy()
        task_id = data.get('task_id')
        if not task_id:
            return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(CrmTask, pk=task_id)
        if task.job_id != pk:
            return Response({'error': 'Задача не принадлежит проекту'}, status=status.HTTP_400_BAD_REQUEST)

        task.title = data.get('title', task.title)
        task.description = data.get('description', task.description)
        task.task_type = data.get('task_type', task.task_type)
        task.assigned_to = data.get('assigned_to', task.assigned_to)
        task.subtasks = json.loads(data.get('subtasks', '[]'))
        task.save()

        if comment_text := data.get('comment'):
            CrmTaskComment.objects.create(task=task, author='newcomp@gmail.com', text=comment_text)

        keep_ids = json.loads(data.get('files_to_keep', '[]'))
        CrmTaskFile.objects.filter(task=task).exclude(id__in=keep_ids).delete()

        for f in request.FILES.getlist('files'):
            CrmTaskFile.objects.create(task=task, file=f)

        return Response({'success': True, 'updated': task.id}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)

        task = get_object_or_404(CrmTask, pk=task_id)
        if task.job_id != pk:
            return Response({'error': 'Задача не принадлежит проекту'}, status=status.HTTP_400_BAD_REQUEST)

        task.delete()
        return Response({'success': True}, status=status.HTTP_200_OK)




from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from .models_crm import CrmTask
from .serializers import CrmTaskSerializer  # если есть сериализатор

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def all_crm_tasks(request):
    tasks = CrmTask.objects.all().prefetch_related('crm_comments', 'crm_files')
    data = []
    for t in tasks:
        data.append({
            'id': t.id,
            'job_id': t.job.id,
            'title': t.title,
            'description': t.description,
            'date_description': getattr(t, 'date_description', None),  # на всякий случай
            'task_type': t.task_type,
            'assigned_to': t.assigned_to,
            'subtasks': t.subtasks,
            'comments': [
                {'author': c.author, 'text': c.text, 'created_at': c.created_at}
                for c in t.crm_comments.all()
            ],
            'files': [f.file.url for f in t.crm_files.all()],
        })
    return Response(data)
    
# CRM API Views
class CrmJobViewSet(viewsets.ModelViewSet):
    
    queryset = CrmJob.objects.all()
    serializer_class = CrmJobSerializer


class CrmTaskViewSet(viewsets.ModelViewSet):
    queryset = CrmTask.objects.all()
    serializer_class = CrmTaskSerializer


class CrmTaskCommentViewSet(viewsets.ModelViewSet):
    queryset = CrmTaskComment.objects.all()
    serializer_class = CrmTaskCommentSerializer


class CrmTaskFileViewSet(viewsets.ModelViewSet):
    queryset = CrmTaskFile.objects.all()
    serializer_class = CrmTaskFileSerializer


class CrmJobListCreateView(generics.ListCreateAPIView):
    queryset = CrmJob.objects.all()
    serializer_class = CrmJobSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CrmJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CrmJob.objects.all()
    serializer_class = CrmJobSerializer
    permission_classes = [permissions.AllowAny]


