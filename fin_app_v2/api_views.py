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

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import json
from .models_crm import CrmJob, CrmTask, CrmTaskFile, CrmTaskComment

@csrf_exempt
@require_http_methods(["GET", "POST", "PATCH", "DELETE"])
def job_tasks_crud(request, pk):
    try:
        job = get_object_or_404(CrmJob, pk=pk)

        if request.method == "GET":
            tasks = CrmTask.objects.filter(job=job).prefetch_related('crm_comments', 'crm_files')
            data = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "task_type": t.task_type,
                    "assigned_to": t.assigned_to,
                    "subtasks": t.subtasks,
                    "job": t.job.id,
                    "comments": [
                        {"author": c.author, "text": c.text, "created_at": c.created_at.isoformat()}
                        for c in t.crm_comments.all()
                    ],
                    "files": [{"id": f.id, "url": f.file.url} for f in t.crm_files.all()],
                }
                for t in tasks
            ]
            return JsonResponse(data, safe=False)

        elif request.method == "POST":
            if request.content_type.startswith("multipart/form-data"):
                data = json.loads(request.POST.get("data", "{}"))
                files = request.FILES.getlist("files")
            else:
                data = json.loads(request.body)
                files = []

            task = CrmTask.objects.create(
                job=job,
                title=data.get("title", ""),
                description=data.get("description", ""),
                task_type=data.get("task_type", "SIMPLE"),
                assigned_to=data.get("assigned_to", ""),
                subtasks=data.get("subtasks", []),
            )

            for f in files:
                CrmTaskFile.objects.create(task=task, file=f)

            if "comment" in data:
                CrmTaskComment.objects.create(task=task, author=job.client_email, text=data["comment"])

            return JsonResponse({"id": task.id, "message": "Task created"}, status=201)

        elif request.method == "PATCH":
            if request.content_type.startswith("multipart/form-data"):
                data_str = request.POST.get("data", "{}")
                data = json.loads(data_str)
                files = request.FILES.getlist("files")
            else:
                data = json.loads(request.body)
                files = []

            task_id = data.get("task_id")
            if not task_id:
                return JsonResponse({"error": "task_id required"}, status=400)

            task = get_object_or_404(CrmTask, id=task_id, job=job)

            task.title = data.get("title", task.title)
            task.description = data.get("description", task.description)
            task.task_type = data.get("task_type", task.task_type)
            task.assigned_to = data.get("assigned_to", task.assigned_to)
            task.subtasks = data.get("subtasks", task.subtasks)
            task.save()

            files_to_keep = data.get("files_to_keep", [])
            existing_files = CrmTaskFile.objects.filter(task=task)
            for f in existing_files:
                if f.id not in files_to_keep:
                    f.delete()
            for f in files:
                CrmTaskFile.objects.create(task=task, file=f)

            return JsonResponse({"message": "Task updated"})

        elif request.method == "DELETE":
            if request.content_type.startswith("multipart/form-data"):
                data = json.loads(request.POST.get("data", "{}"))
            else:
                data = json.loads(request.body)

            task_id = data.get("task_id")
            if not task_id:
                return JsonResponse({"error": "task_id required"}, status=400)

            task = get_object_or_404(CrmTask, id=task_id, job=job)
            task.delete()
            return JsonResponse({"message": "Task deleted"})

        return JsonResponse({"error": "Method not allowed"}, status=405)

    except Exception as e:
        print("Exception in job_tasks_crud:", str(e))
        return JsonResponse({"error": str(e)}, status=500)


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


