# # api_views.py - CREATE THIS AS A NEW FILE
# # This file doesn't exist in your project, so it's 100% safe to add
#
# from django.http import JsonResponse
# from rest_framework import generics, status, permissions
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.response import Response
# from django.contrib.auth.models import User
# from django.db.models import Sum, Count, Q, F
# from django.utils import timezone
# from datetime import timedelta
# from .models import Job, Task, DeductionLog, calculate_income_balance
# from .serializers import (
#     JobSerializer, TaskSerializer, UserSerializer,
#     DeductionLogSerializer, DashboardStatsSerializer
# )
# from rest_framework import viewsets
# from .models_crm import CrmJob, CrmTask, CrmTaskComment, CrmTaskFile
# from .serializers import CrmJobSerializer, CrmTaskSerializer, CrmTaskCommentSerializer, CrmTaskFileSerializer
#
#
# class IsAdminUser(permissions.BasePermission):
#     """Custom permission to only allow admin users."""
#
#     def has_permission(self, request, view):
#         return request.user.is_authenticated and request.user.email == 'Admin@dbr.org'
#
#
# # Job API Views
# class JobListCreateView(generics.ListCreateAPIView):
#     queryset = Job.objects.all()
#     serializer_class = JobSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         queryset = Job.objects.all()
#         # Filter by status if provided
#         status_filter = self.request.query_params.get('status', None)
#         if status_filter == 'completed':
#             # Jobs with all tasks completed
#             queryset = queryset.filter(tasks__progress=100).distinct()
#         elif status_filter == 'in_progress':
#             # Jobs with at least one task in progress
#             queryset = queryset.filter(tasks__progress__gt=0, tasks__progress__lt=100).distinct()
#         elif status_filter == 'overdue':
#             # Jobs with overdue tasks
#             today = timezone.now().date()
#             queryset = queryset.filter(tasks__deadline__lt=today, tasks__progress__lt=100).distinct()
#
#         return queryset.order_by('-created_at')
#
#
# class JobDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Job.objects.all()
#     serializer_class = JobSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def destroy(self, request, *args, **kwargs):
#         # Only admin can delete jobs
#         if request.user.email != 'Admin@dbr.org':
#             return Response(
#                 {'error': 'Permission denied'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().destroy(request, *args, **kwargs)
#
#
# # Task API Views
# class TaskListCreateView(generics.ListCreateAPIView):
#     serializer_class = TaskSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         queryset = Task.objects.select_related('job').prefetch_related('assigned_users')
#
#         # Filter by job if provided
#         job_id = self.request.query_params.get('job', None)
#         if job_id:
#             queryset = queryset.filter(job_id=job_id)
#
#         # Filter by assigned user
#         user_id = self.request.query_params.get('user', None)
#         if user_id:
#             queryset = queryset.filter(assigned_users__id=user_id)
#
#         # Filter by status
#         status_filter = self.request.query_params.get('status', None)
#         if status_filter == 'completed':
#             queryset = queryset.filter(progress=100)
#         elif status_filter == 'in_progress':
#             queryset = queryset.filter(progress__gt=0, progress__lt=100)
#         elif status_filter == 'pending':
#             queryset = queryset.filter(progress=0)
#         elif status_filter == 'overdue':
#             today = timezone.now().date()
#             queryset = queryset.filter(deadline__lt=today, progress__lt=100)
#
#         # Filter by date range
#         date_from = self.request.query_params.get('date_from', None)
#         date_to = self.request.query_params.get('date_to', None)
#         if date_from:
#             queryset = queryset.filter(deadline__gte=date_from)
#         if date_to:
#             queryset = queryset.filter(deadline__lte=date_to)
#
#         return queryset.order_by('deadline')
#
#
# class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def update(self, request, *args, **kwargs):
#         # Check if user can update this task
#         task = self.get_object()
#         if (request.user not in task.assigned_users.all() and
#                 request.user.email != 'Admin@dbr.org'):
#             return Response(
#                 {'error': 'Permission denied'},
#                 status=status.HTTP_403_FORBIDDEN
#             )
#         return super().update(request, *args, **kwargs)
#
#
# # Developer Task Views
# class DeveloperTasksView(generics.ListAPIView):
#     serializer_class = TaskSerializer
#     permission_classes = [permissions.AllowAny]
#
#     def get_queryset(self):
#         return Task.objects.filter(
#             assigned_users=self.request.user
#         ).select_related('job').order_by('deadline')
#
#
# # Dashboard API Views
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def dashboard_stats(request):
#     """Get dashboard statistics"""
#     today = timezone.now().date()
#     current_month = today.month
#     current_year = today.year
#
#     # Basic project stats
#     total_projects = Job.objects.count()
#
#     # Project status counts
#     in_progress_projects = Job.objects.filter(
#         tasks__progress__gt=0, tasks__progress__lt=100
#     ).distinct().count()
#
#     completed_projects = Job.objects.filter(
#         tasks__progress=100
#     ).distinct().count()
#
#     overdue_projects = Job.objects.filter(
#         tasks__deadline__lt=today, tasks__progress__lt=100
#     ).distinct().count()
#
#     # Financial data
#     total_revenue = Job.objects.aggregate(
#         total=Sum('over_all_income')
#     )['total'] or 0
#
#     monthly_income = Job.objects.filter(
#         created_at__year=current_year,
#         created_at__month=current_month
#     ).aggregate(total=Sum('over_all_income'))['total'] or 0
#
#     # Get income balance
#     balance_data = calculate_income_balance()
#     income_balance = balance_data['income_balance']
#
#     # Task and user counts
#     total_customers = User.objects.count()
#     total_transactions = Task.objects.filter(paid=True).count()
#     total_products = Task.objects.count()
#
#     stats = {
#         'total_projects': total_projects,
#         'in_progress_projects': in_progress_projects,
#         'completed_projects': completed_projects,
#         'overdue_projects': overdue_projects,
#         'total_revenue': total_revenue,
#         'total_customers': total_customers,
#         'total_transactions': total_transactions,
#         'total_products': total_products,
#         'monthly_income': monthly_income,
#         'income_balance': income_balance,
#     }
#
#     serializer = DashboardStatsSerializer(stats)
#     return Response(serializer.data)
#
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def monthly_revenue_chart(request):
#     """Get monthly revenue data for charts"""
#     from datetime import datetime
#     import calendar
#
#     # Get current year or specified year
#     year = int(request.query_params.get('year', timezone.now().year))
#
#     monthly_data = []
#     for month in range(1, 13):
#         # Get jobs created in this month
#         jobs_income = Job.objects.filter(
#             created_at__year=year,
#             created_at__month=month
#         ).aggregate(Sum('over_all_income'))['over_all_income__sum'] or 0
#
#         # Get expenses (money paid to developers)
#         expenses = Task.objects.filter(
#             job__created_at__year=year,
#             job__created_at__month=month,
#             paid=True
#         ).aggregate(Sum('money_for_task'))['money_for_task__sum'] or 0
#
#         profit = jobs_income - expenses
#
#         monthly_data.append({
#             'month': calendar.month_abbr[month],
#             'income': jobs_income,
#             'expenses': expenses,
#             'profit': profit
#         })
#
#     return Response(monthly_data)
#
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def project_status_distribution(request):
#     """Get project status distribution for pie chart"""
#     today = timezone.now().date()
#
#     # Count projects by status
#     in_progress = Job.objects.filter(
#         tasks__progress__gt=0, tasks__progress__lt=100
#     ).distinct().count()
#
#     completed = Job.objects.filter(
#         tasks__progress=100
#     ).distinct().count()
#
#     overdue = Job.objects.filter(
#         tasks__deadline__lt=today, tasks__progress__lt=100
#     ).distinct().count()
#
#     data = [
#         {'status': 'В ходе выполнения', 'count': in_progress, 'percentage': 58.33},
#         {'status': 'Законченный', 'count': completed, 'percentage': 25},
#         {'status': 'Незаконченный', 'count': overdue, 'percentage': 8}
#     ]
#
#     return Response(data)
#
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def recent_projects(request):
#     """Get recent projects for dashboard"""
#     recent_jobs = Job.objects.order_by('-created_at')[:5]
#     serializer = JobSerializer(recent_jobs, many=True)
#     return Response(serializer.data)
#
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def upcoming_deadlines(request):
#     """Get upcoming task deadlines"""
#     today = timezone.now().date()
#     upcoming_tasks = Task.objects.filter(
#         progress__lt=100,
#         deadline__gte=today
#     ).select_related('job').order_by('deadline')[:10]
#
#     serializer = TaskSerializer(upcoming_tasks, many=True)
#     return Response(serializer.data)
#
#
# # Calendar API Views
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def calendar_tasks(request):
#     """Get tasks for calendar view"""
#     year = int(request.query_params.get('year', timezone.now().year))
#     month = int(request.query_params.get('month', timezone.now().month))
#
#     # Get tasks for the specified month
#     tasks = Task.objects.filter(
#         deadline__year=year,
#         deadline__month=month
#     ).select_related('job')
#
#     # Group tasks by date
#     tasks_by_date = {}
#     for task in tasks:
#         date_key = task.deadline.strftime('%Y-%m-%d')
#         if date_key not in tasks_by_date:
#             tasks_by_date[date_key] = []
#         tasks_by_date[date_key].append({
#             'id': task.id,
#             'title': task.title,
#             'progress': task.progress,
#             'job_title': task.job.title,
#             'status_color': TaskSerializer().get_status_color(task)
#         })
#
#     return Response(tasks_by_date)
#
#
#
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status, permissions, parsers
# from django.shortcuts import get_object_or_404, render
# from .models_crm import CrmJob, CrmTask, CrmTaskFile, CrmTaskComment
# from .serializers import CrmTaskSerializer, CrmTaskFileSerializer, CrmTaskCommentSerializer
# import json
#
#
# class JobTaskCrudAPIView(APIView):
#     permission_classes = [permissions.AllowAny]
#     parser_classes = [parsers.MultiPartParser, parsers.JSONParser]
#
#     def get(self, request, pk):
#         tasks = CrmTask.objects.filter(job_id=pk).order_by('-id')
#         serializer = CrmTaskSerializer(tasks, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request, pk):
#         data = request.data.copy()
#         subtasks = json.loads(data.get('subtasks', '[]'))
#         files = request.FILES.getlist('files')
#
#         task = CrmTask.objects.create(
#             job_id=pk,
#             title=data.get('title', ''),
#             description=data.get('description', ''),
#             task_type=data.get('task_type', 'SIMPLE'),
#             assigned_to=data.get('assigned_to', ''),
#             subtasks=subtasks
#         )
#
#         if comment_text := data.get('comment'):
#             CrmTaskComment.objects.create(task=task, author='newcomp@gmail.com', text=comment_text)
#
#         for file in files:
#             CrmTaskFile.objects.create(task=task, file=file)
#
#         return Response({'success': True, 'id': task.id}, status=status.HTTP_201_CREATED)
#
#     def patch(self, request, pk):
#         data = request.data.copy()
#         task_id = data.get('task_id')
#         if not task_id:
#             return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         task = get_object_or_404(CrmTask, pk=task_id)
#         if task.job_id != pk:
#             return Response({'error': 'Задача не принадлежит проекту'}, status=status.HTTP_400_BAD_REQUEST)
#
#         task.title = data.get('title', task.title)
#         task.description = data.get('description', task.description)
#         task.task_type = data.get('task_type', task.task_type)
#         task.assigned_to = data.get('assigned_to', task.assigned_to)
#         task.subtasks = json.loads(data.get('subtasks', '[]'))
#         task.save()
#
#         if comment_text := data.get('comment'):
#             CrmTaskComment.objects.create(task=task, author='newcomp@gmail.com', text=comment_text)
#
#         keep_ids = json.loads(data.get('files_to_keep', '[]'))
#         CrmTaskFile.objects.filter(task=task).exclude(id__in=keep_ids).delete()
#
#         for f in request.FILES.getlist('files'):
#             CrmTaskFile.objects.create(task=task, file=f)
#
#         return Response({'success': True, 'updated': task.id}, status=status.HTTP_200_OK)
#
#     def delete(self, request, pk):
#         task_id = request.data.get('task_id')
#         if not task_id:
#             return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)
#
#         task = get_object_or_404(CrmTask, pk=task_id)
#         if task.job_id != pk:
#             return Response({'error': 'Задача не принадлежит проекту'}, status=status.HTTP_400_BAD_REQUEST)
#
#         task.delete()
#         return Response({'success': True}, status=status.HTTP_200_OK)
#
#
#
#
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import permissions
# from django.shortcuts import get_object_or_404
# from .models_crm import CrmTask
# from .serializers import CrmTaskSerializer  # если есть сериализатор
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def all_crm_tasks(request):
#     tasks = CrmTask.objects.all().prefetch_related('crm_comments', 'crm_files')
#     data = []
#     for t in tasks:
#         data.append({
#             'id': t.id,
#             'job_id': t.job.id,
#             'title': t.title,
#             'description': t.description,
#             'date_description': getattr(t, 'date_description', None),  # на всякий случай
#             'task_type': t.task_type,
#             'assigned_to': t.assigned_to,
#             'subtasks': t.subtasks,
#             'comments': [
#                 {'author': c.author, 'text': c.text, 'created_at': c.created_at}
#                 for c in t.crm_comments.all()
#             ],
#             'files': [f.file.url for f in t.crm_files.all()],
#         })
#     return Response(data)
#
# # CRM API Views
# class CrmJobViewSet(viewsets.ModelViewSet):
#
#     queryset = CrmJob.objects.all()
#     serializer_class = CrmJobSerializer
#
#
# class CrmTaskViewSet(viewsets.ModelViewSet):
#     queryset = CrmTask.objects.all()
#     serializer_class = CrmTaskSerializer
#
#
# class CrmTaskCommentViewSet(viewsets.ModelViewSet):
#     queryset = CrmTaskComment.objects.all()
#     serializer_class = CrmTaskCommentSerializer
#
#
# class CrmTaskFileViewSet(viewsets.ModelViewSet):
#     queryset = CrmTaskFile.objects.all()
#     serializer_class = CrmTaskFileSerializer
#
#
# # class CrmJobListCreateView(generics.ListCreateAPIView):
# #     queryset = CrmJob.objects.all()
# #     serializer_class = CrmJobSerializer
# #     permission_classes = [permissions.AllowAny]
# #
# #     def create(self, request, *args, **kwargs):
# #         serializer = self.get_serializer(data=request.data)
# #         if not serializer.is_valid():
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# #         self.perform_create(serializer)
# #         headers = self.get_success_headers(serializer.data)
# #         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
#
#
#
# # ADD THESE TO THE END OF YOUR EXISTING api_views.py FILE
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def get_existing_jobs(request):
#     """Get existing jobs for dropdown"""
#     jobs = Job.objects.all().order_by('-created_at')
#     return Response([{
#         'id': job.id,
#         'title': job.title,
#         'client_email': job.client_email,
#         'created_at': job.created_at.strftime('%Y-%m-%d'),
#         'income': job.over_all_income
#     } for job in jobs])
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def get_job_details(request):
#     """Get specific job details"""
#     job_id = request.GET.get('job_id')
#     if not job_id:
#         return Response({'error': 'job_id required'}, status=400)
#     try:
#         job = Job.objects.get(id=job_id)
#         return Response({
#             'title': job.title,
#             'client_email': job.client_email,
#             'created_at': job.created_at.strftime('%Y-%m-%d'),
#             'income': job.over_all_income
#         })
#     except Job.DoesNotExist:
#         return Response({'error': 'Job not found'}, status=404)
#
# @api_view(['GET'])
# @permission_classes([permissions.AllowAny])
# def get_company_suggestions(request):
#     """Get company suggestions for autocomplete"""
#     suggestions = list(Job.objects.values_list('title', flat=True).distinct())
#     return Response({'suggestions': suggestions})
#
# def crm_form_view(request):
#     return render(request, 'crm_form.html')
#
#
#
# class CrmJobDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = CrmJob.objects.all()
#     serializer_class = CrmJobSerializer
#     permission_classes = [permissions.AllowAny]
#
#


# api_views.py - COMPLETE FINAL VERSION

from django.http import JsonResponse, HttpResponseRedirect
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, parsers
from django.shortcuts import get_object_or_404, render
import json
import os


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


# ENHANCED CRM Task CRUD API with 100MB file support
class JobTaskCrudAPIView(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [parsers.MultiPartParser, parsers.JSONParser, parsers.FormParser]

    def get(self, request, pk):
        """Get all tasks with enhanced file information"""
        try:
            tasks = CrmTask.objects.filter(job_id=pk).prefetch_related('crm_comments', 'crm_files').order_by(
                '-created_at')

            tasks_data = []
            for task in tasks:
                task_data = {
                    'id': task.id,
                    'title': task.title,
                    'description': task.description,
                    'task_type': task.task_type,
                    'assigned_to': task.assigned_to,
                    'subtasks': task.subtasks,
                    'created_at': task.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'updated_at': task.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                    'comments': [
                        {
                            'id': comment.id,
                            'author': comment.author,
                            'text': comment.text,
                            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        for comment in task.crm_comments.all()
                    ],
                    'files': [
                        {
                            'id': file_obj.id,
                            'filename': file_obj.filename,
                            'file_url': file_obj.file.url,
                            'file_size_mb': file_obj.file_size_mb,
                            'file_extension': file_obj.file_extension,
                            'is_image': file_obj.is_image,
                            'is_document': file_obj.is_document,
                            'is_video': file_obj.is_video,
                            'uploaded_at': file_obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'uploaded_by': file_obj.uploaded_by
                        }
                        for file_obj in task.crm_files.all()
                    ]
                }
                tasks_data.append(task_data)

            return Response(tasks_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, pk):
        """Create new task with files (100MB support)"""
        try:
            data = request.data.copy()

            # Parse subtasks
            subtasks = request.data.getlist('subtasks')

            # Create task
            task = CrmTask.objects.create(
                job_id=pk,
                title=data.get('title', ''),
                description=data.get('description', ''),
                task_type=data.get('task_type', 'SIMPLE'),
                assigned_to=data.get('assigned_to', ''),
                subtasks=subtasks
            )

            # Add comment
            if data.get('comment'):
                CrmTaskComment.objects.create(
                    task=task,
                    author=data.get('author', 'system@example.com'),
                    text=data.get('comment')
                )

            # Upload files with 100MB support
            uploaded_files = []
            files = request.FILES.getlist('files')
            for file_obj in files:
                # File validation is handled by model validators
                task_file = CrmTaskFile.objects.create(
                    task=task,
                    file=file_obj,
                    uploaded_by=data.get('author', 'system@example.com')
                )
                uploaded_files.append({
                    'id': task_file.id,
                    'filename': task_file.filename,
                    'file_url': task_file.file.url,
                    'file_size_mb': task_file.file_size_mb,
                    'file_extension': task_file.file_extension
                })

            return Response({
                'success': True,
                'id': task.id,
                'uploaded_files': uploaded_files,
                'message': f'Task created with {len(uploaded_files)} files'
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, pk):
        """Update task with enhanced file management"""
        try:
            data = request.data.copy()
            task_id = data.get('task_id')

            if not task_id:
                return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)

            task = get_object_or_404(CrmTask, pk=task_id, job_id=pk)

            # Update task fields
            task.title = data.get('title', task.title)
            task.description = data.get('description', task.description)
            task.task_type = data.get('task_type', task.task_type)
            task.assigned_to = data.get('assigned_to', task.assigned_to)

            # Update subtasks
            task.subtasks = request.data.getlist('subtasks')

            task.save()

            # Add new comment
            if data.get('comment'):
                CrmTaskComment.objects.create(
                    task=task,
                    author=data.get('author', 'system@example.com'),
                    text=data.get('comment')
                )

            # Handle file management
            files_to_keep_data = data.get('files_to_keep', '[]')
            if isinstance(files_to_keep_data, str):
                try:
                    files_to_keep = json.loads(files_to_keep_data)
                except:
                    files_to_keep = []
            else:
                files_to_keep = files_to_keep_data

            # Delete files not in keep list
            files_deleted = task.crm_files.exclude(id__in=files_to_keep)
            deleted_count = files_deleted.count()
            files_deleted.delete()

            # Add new files
            uploaded_files = []
            new_files = request.FILES.getlist('files')
            for file_obj in new_files:
                task_file = CrmTaskFile.objects.create(
                    task=task,
                    file=file_obj,
                    uploaded_by=data.get('author', 'system@example.com')
                )
                uploaded_files.append({
                    'id': task_file.id,
                    'filename': task_file.filename,
                    'file_url': task_file.file.url,
                    'file_size_mb': task_file.file_size_mb
                })

            return Response({
                'success': True,
                'updated': task.id,
                'files_deleted': deleted_count,
                'files_uploaded': len(uploaded_files),
                'uploaded_files': uploaded_files
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, pk):
        """Delete task and all associated files"""
        try:
            task_id = request.data.get('task_id')
            if not task_id:
                return Response({'error': 'task_id required'}, status=status.HTTP_400_BAD_REQUEST)

            task = get_object_or_404(CrmTask, pk=task_id, job_id=pk)

            # Count files before deletion
            files_count = task.crm_files.count()

            # Delete task (files will be deleted automatically due to CASCADE)
            task.delete()

            return Response({
                'success': True,
                'message': f'Task and {files_count} files deleted successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Individual File Management APIs
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def add_files_to_task(request, task_id):
    """Add files to existing task (100MB support)"""
    try:
        task = get_object_or_404(CrmTask, pk=task_id)

        uploaded_files = []
        files = request.FILES.getlist('files')

        if not files:
            return Response({'error': 'No files provided'}, status=status.HTTP_400_BAD_REQUEST)

        for file_obj in files:
            # File validation is handled by model validators (100MB limit)
            task_file = CrmTaskFile.objects.create(
                task=task,
                file=file_obj,
                uploaded_by=request.data.get('uploaded_by', 'system@example.com')
            )
            uploaded_files.append({
                'id': task_file.id,
                'filename': task_file.filename,
                'file_url': task_file.file.url,
                'file_size_mb': task_file.file_size_mb,
                'uploaded_at': task_file.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')
            })

        return Response({
            'success': True,
            'uploaded_files': uploaded_files,
            'total_uploaded': len(uploaded_files),
            'message': f'{len(uploaded_files)} files uploaded successfully to task "{task.title}"'
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([permissions.AllowAny])
def delete_file_from_task(request, task_id, file_id):
    """Delete specific file from task"""
    try:
        task = get_object_or_404(CrmTask, pk=task_id)
        file_obj = get_object_or_404(CrmTaskFile, pk=file_id, task=task)

        filename = file_obj.filename
        file_size_mb = file_obj.file_size_mb

        # Delete the file
        file_obj.delete()

        return Response({
            'success': True,
            'message': f'File "{filename}" ({file_size_mb}MB) deleted successfully',
            'deleted_file': {
                'id': file_id,
                'filename': filename,
                'file_size_mb': file_size_mb
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_task_files(request, task_id):
    """Get all files for a specific task"""
    try:
        task = get_object_or_404(CrmTask, pk=task_id)
        files = task.crm_files.all().order_by('-uploaded_at')

        files_data = []
        total_size_mb = 0

        for file_obj in files:
            file_data = {
                'id': file_obj.id,
                'filename': file_obj.filename,
                'file_url': file_obj.file.url,
                'file_size_mb': file_obj.file_size_mb,
                'file_extension': file_obj.file_extension,
                'is_image': file_obj.is_image,
                'is_document': file_obj.is_document,
                'is_video': file_obj.is_video,
                'uploaded_at': file_obj.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                'uploaded_by': file_obj.uploaded_by
            }
            files_data.append(file_data)
            total_size_mb += file_obj.file_size_mb

        return Response({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title
            },
            'files': files_data,
            'total_files': len(files_data),
            'total_size_mb': round(total_size_mb, 2)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def bulk_delete_files(request, task_id):
    """Delete multiple files at once"""
    try:
        task = get_object_or_404(CrmTask, pk=task_id)
        file_ids = request.data.get('file_ids', [])

        if not file_ids:
            return Response({'error': 'No file IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        files_to_delete = task.crm_files.filter(id__in=file_ids)

        if not files_to_delete.exists():
            return Response({'error': 'No files found with provided IDs'}, status=status.HTTP_404_NOT_FOUND)

        # Collect file info before deletion
        deleted_files = []
        total_size_deleted = 0

        for file_obj in files_to_delete:
            deleted_files.append({
                'id': file_obj.id,
                'filename': file_obj.filename,
                'file_size_mb': file_obj.file_size_mb
            })
            total_size_deleted += file_obj.file_size_mb

        # Delete files
        deleted_count = files_to_delete.count()
        files_to_delete.delete()

        return Response({
            'success': True,
            'message': f'{deleted_count} files deleted successfully',
            'deleted_files': deleted_files,
            'total_deleted': deleted_count,
            'total_size_deleted_mb': round(total_size_deleted, 2)
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def download_file(request, task_id, file_id):
    """Download a specific file"""
    try:
        task = get_object_or_404(CrmTask, pk=task_id)
        file_obj = get_object_or_404(CrmTaskFile, pk=file_id, task=task)

        # Redirect to file URL for download
        return HttpResponseRedirect(file_obj.file.url)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_storage_stats(request):
    """Get storage statistics for all CRM files"""
    try:
        # Get file statistics
        stats = CrmTaskFile.objects.aggregate(
            total_files=Count('id'),
            total_size_bytes=Sum('file__size')
        )

        total_files = stats['total_files'] or 0
        total_size_bytes = stats['total_size_bytes'] or 0
        total_size_mb = round(total_size_bytes / (1024 * 1024), 2)
        total_size_gb = round(total_size_mb / 1024, 2)

        # Get file type breakdown
        file_types = {}
        files = CrmTaskFile.objects.all()

        for file_obj in files:
            ext = file_obj.file_extension
            if ext in file_types:
                file_types[ext]['count'] += 1
                file_types[ext]['size_mb'] += file_obj.file_size_mb
            else:
                file_types[ext] = {
                    'count': 1,
                    'size_mb': file_obj.file_size_mb
                }

        return Response({
            'success': True,
            'storage_stats': {
                'total_files': total_files,
                'total_size_mb': total_size_mb,
                'total_size_gb': total_size_gb,
                'file_types': file_types
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def all_crm_tasks(request):
    """Get all CRM tasks with files and comments"""
    tasks = CrmTask.objects.all().prefetch_related('crm_comments', 'crm_files')
    data = []
    for t in tasks:
        data.append({
            'id': t.id,
            'job_id': t.job.id,
            'title': t.title,
            'description': t.description,
            'task_type': t.task_type,
            'assigned_to': t.assigned_to,
            'subtasks': t.subtasks,
            'comments': [
                {'author': c.author, 'text': c.text, 'created_at': c.created_at}
                for c in t.crm_comments.all()
            ],
            'files': [
                {
                    'id': f.id,
                    'filename': f.filename,
                    'file_url': f.file.url,
                    'file_size_mb': f.file_size_mb
                }
                for f in t.crm_files.all()
            ],
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


# Enhanced CRM Job List/Create with job linking
class CrmJobListCreateView(generics.ListCreateAPIView):
    queryset = CrmJob.objects.all()
    serializer_class = CrmJobSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        # Handle existing job linking
        existing_job_id = data.get('existing_job_id')
        if existing_job_id:
            try:
                existing_job = Job.objects.get(id=existing_job_id)
                if not data.get('client_email'):
                    data['client_email'] = existing_job.client_email
                if not data.get('client_company_name'):
                    data['client_company_name'] = existing_job.title
                data['existing_job'] = existing_job_id
            except Job.DoesNotExist:
                return Response({'error': 'Selected job does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CrmJobDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CrmJob.objects.all()
    serializer_class = CrmJobSerializer
    permission_classes = [permissions.AllowAny]


# Helper endpoints for CRM form
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_existing_jobs(request):
    """Get existing jobs for dropdown"""
    jobs = Job.objects.all().order_by('-created_at')
    return Response([{
        'id': job.id,
        'title': job.title,
        'client_email': job.client_email,
        'created_at': job.created_at.strftime('%Y-%m-%d'),
        'income': job.over_all_income
    } for job in jobs])


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_job_details(request):
    """Get specific job details"""
    job_id = request.GET.get('job_id')
    if not job_id:
        return Response({'error': 'job_id required'}, status=400)
    try:
        job = Job.objects.get(id=job_id)
        return Response({
            'title': job.title,
            'client_email': job.client_email,
            'created_at': job.created_at.strftime('%Y-%m-%d'),
            'income': job.over_all_income
        })
    except Job.DoesNotExist:
        return Response({'error': 'Job not found'}, status=404)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_company_suggestions(request):
    """Get company suggestions for autocomplete"""
    suggestions = list(Job.objects.values_list('title', flat=True).distinct())
    return Response({'suggestions': suggestions})


def crm_form_view(request):
    """Render CRM form template"""
    return render(request, 'crm_form.html')