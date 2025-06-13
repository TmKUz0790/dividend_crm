from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum
from django.utils.dateparse import parse_date
import json

from .models_crm import CrmJob

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_get_all_jobs(request):
    if request.method == "GET":
        jobs = CrmJob.objects.all()
        jobs_data = []
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'client_email': job.client_email,
                'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
                'full_name': job.full_name,
                'phone_number': job.phone_number,
                'position': job.position,
                'client_company_name': job.client_company_name,
                'client_company_phone': job.client_company_phone,
                'client_company_address': job.client_company_address,
                'client_website': job.client_website,
                'project_count': job.crm_tasks.count(),
                'task_count': job.crm_tasks.count(),
            })
        return JsonResponse(jobs_data, safe=False)
    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        required_fields = ['title', 'client_email', 'over_all_income']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return JsonResponse({'error': f"Missing: {', '.join(missing_fields)}"}, status=400)
        try:
            over_all_income = float(data['over_all_income'])
        except ValueError:
            return JsonResponse({'error': 'over_all_income must be a number'}, status=400)
        job = CrmJob.objects.create(
            client_email=data['client_email'],
            full_name=data.get('full_name', ''),
            phone_number=data.get('phone_number', ''),
            position=data.get('position', ''),
            client_company_name=data.get('client_company_name', ''),
            client_company_phone=data.get('client_company_phone', ''),
            client_company_address=data.get('client_company_address', ''),
            client_website=data.get('client_website', ''),
            status=data.get('status', 'active'),  # добавлено поле status
        )
        job_data = {
            'id': job.id,
            'client_email': job.client_email,
            'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
            'full_name': job.full_name,
            'phone_number': job.phone_number,
            'position': job.position,
            'client_company_name': job.client_company_name,
            'client_company_phone': job.client_company_phone,
            'client_company_address': job.client_company_address,
            'client_website': job.client_website,
            'project_count': job.crm_tasks.count(),
            'task_count': job.crm_tasks.count(),
        }
        return JsonResponse(job_data, status=201)

@csrf_exempt
@require_http_methods(["GET"])
def api_get_job_detail(request, job_id):
    job = get_object_or_404(CrmJob, id=job_id)
    job_data = {
        'id': job.id,
        'client_email': job.client_email,
        'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
        'full_name': job.full_name,
        'phone_number': job.phone_number,
        'position': job.position,
        'client_company_name': job.client_company_name,
        'client_company_phone': job.client_company_phone,
        'client_company_address': job.client_company_address,
        'client_website': job.client_website,
        'project_count': job.crm_tasks.count(),
        'task_count': job.crm_tasks.count(),
    }
    return JsonResponse(job_data)

@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_update_job(request, job_id):
    job = get_object_or_404(CrmJob, id=job_id)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    for field in [ 'client_email', 'full_name', 'phone_number', 'position', 'client_company_name', 'client_company_phone', 'client_company_address', 'client_website']:
        if field in data:
            setattr(job, field, data[field])


    job.save()
    job_data = {
        'id': job.id,
        'client_email': job.client_email,
        'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
        'full_name': job.full_name,
        'phone_number': job.phone_number,
        'position': job.position,
        'client_company_name': job.client_company_name,
        'client_company_phone': job.client_company_phone,
        'client_company_address': job.client_company_address,
        'client_website': job.client_website,
        'project_count': job.crm_tasks.count(),
        'task_count': job.crm_tasks.count(),
    }
    return JsonResponse(job_data)

@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_job(request, job_id):
    job = get_object_or_404(CrmJob, id=job_id)
    job.delete()
    return HttpResponse(status=204)
