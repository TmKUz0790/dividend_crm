# fast_api_views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
import json

from .models import Job, Task


@csrf_exempt
@require_http_methods(["GET", "POST"])
def jobs_api(request):
    if request.method == 'GET':
        # List all jobs
        jobs = Job.objects.all().order_by('-created_at')
        data = []
        for job in jobs:
            data.append({
                'id': job.id,
                'title': job.title,
                'client_email': job.client_email,
                'over_all_income': job.over_all_income,
                'created_at': job.created_at
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        # Create new job
        data = json.loads(request.body)
        job = Job.objects.create(
            title=data.get('title'),
            client_email=data.get('client_email'),
            over_all_income=data.get('over_all_income', 0)
        )
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'client_email': job.client_email,
            'over_all_income': job.over_all_income,
            'created_at': job.created_at
        })


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def job_detail_api(request, pk):
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'client_email': job.client_email,
            'over_all_income': job.over_all_income,
            'created_at': job.created_at
        })

    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)
        if 'title' in data:
            job.title = data['title']
        if 'client_email' in data:
            job.client_email = data['client_email']
        if 'over_all_income' in data:
            job.over_all_income = data['over_all_income']
        job.save()

        return JsonResponse({
            'id': job.id,
            'title': job.title,
            'client_email': job.client_email,
            'over_all_income': job.over_all_income,
            'created_at': job.created_at
        })

    elif request.method == 'DELETE':
        job.delete()
        return JsonResponse({'message': 'Job deleted'})


@csrf_exempt
@require_http_methods(["GET"])
def job_tasks_api(request, pk):
    job = get_object_or_404(Job, pk=pk)
    tasks = job.tasks.all()
    data = []
    for task in tasks:
        data.append({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'hours': task.hours,
            'progress': task.progress,
            'task_percentage': task.task_percentage,
            'money_for_task': task.money_for_task,
            'task_type': task.task_type,
            'deadline': task.deadline,
            'job': task.job_id,
            'assigned_email': task.assigned_email,
            'task_status': task.task_status
        })
    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def tasks_api(request):
    if request.method == 'GET':
        job_id = request.GET.get('job_id')
        if not job_id:
            return JsonResponse({'error': 'job_id required'}, status=400)

        job = get_object_or_404(Job, id=job_id)
        tasks = job.tasks.all()
        data = []
        for task in tasks:
            data.append({
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'hours': task.hours,
                'progress': task.progress,
                'task_percentage': task.task_percentage,
                'money_for_task': task.money_for_task,
                'task_type': task.task_type,
                'deadline': task.deadline,
                'job': task.job_id,
                'assigned_email': task.assigned_email,
                'task_status': task.task_status 
            })
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        data = json.loads(request.body)
        job = get_object_or_404(Job, id=data.get('job'))

        task = Task.objects.create(
            job=job,
            title=data.get('title'),
            description=data.get('description', ''),
            hours=data.get('hours', 1),
            task_percentage=data.get('task_percentage', 0),
            money_for_task=data.get('money_for_task', 0),
            task_type=data.get('task_type', 'SIMPLE'),
            deadline=data.get('deadline'),
            assigned_email=data.get('assigned_email'),
            task_status=data.get('task_status', 'Бошланмади')
        )

        return JsonResponse({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'hours': task.hours,
            'progress': task.progress,
            'task_percentage': task.task_percentage,
            'money_for_task': task.money_for_task,
            'task_type': task.task_type,
            'deadline': task.deadline,
            'job': task.job_id,
            'assigned_email': task.assigned_email,
            'task_status': task.task_status  
        })


@csrf_exempt
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def task_detail_api(request, pk):
    task = get_object_or_404(Task, pk=pk)

    if request.method == 'GET':
        return JsonResponse({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'hours': task.hours,
            'progress': task.progress,
            'task_percentage': task.task_percentage,
            'money_for_task': task.money_for_task,
            'task_type': task.task_type,
            'deadline': task.deadline,
            'job': task.job_id,
            'assigned_email': task.assigned_email,
            'task_status': task.task_status  
        })

    elif request.method in ['PUT', 'PATCH']:
        data = json.loads(request.body)

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'hours' in data:
            task.hours = data['hours']
        if 'progress' in data:
            task.progress = data['progress']
        if 'task_percentage' in data:
            task.task_percentage = data['task_percentage']
        if 'money_for_task' in data:
            task.money_for_task = data['money_for_task']
        if 'task_type' in data:
            task.task_type = data['task_type']
        if 'deadline' in data:
            task.deadline = data['deadline']
        if 'assigned_email' in data:
            task.assigned_email = data['assigned_email']
        if 'task_status' in data:
            task.task_status = data['task_status']      

        task.save()

        return JsonResponse({
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'hours': task.hours,
            'progress': task.progress,
            'task_percentage': task.task_percentage,
            'money_for_task': task.money_for_task,
            'task_type': task.task_type,
            'deadline': task.deadline,
            'job': task.job_id,
            'assigned_email': task.assigned_email,
            'task_status': task.task_status             
        })

    elif request.method == 'DELETE':
        task.delete()
        return JsonResponse({'message': 'Task deleted'})