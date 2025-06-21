# from django.http import JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.http import require_http_methods
# from django.shortcuts import get_object_or_404
# from django.contrib.auth.models import User
# from django.db import transaction
# from django.db.models import Sum
# from django.utils.dateparse import parse_date
# import json
#
# from .models_crm import CrmJob
#
# @csrf_exempt
# @require_http_methods(["GET", "POST"])
# def api_get_all_jobs(request):
#     if request.method == "GET":
#         jobs = CrmJob.objects.all()
#         jobs_data = []
#         for job in jobs:
#             jobs_data.append({
#                 'id': job.id,
#                 'client_email': job.client_email,
#                 'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
#                 'full_name': job.full_name,
#                 'phone_number': job.phone_number,
#                 'position': job.position,
#                 'client_company_name': job.client_company_name,
#                 'client_company_phone': job.client_company_phone,
#                 'client_company_address': job.client_company_address,
#                 'client_website': job.client_website,
#                 'project_count': job.crm_tasks.count(),
#                 'task_count': job.crm_tasks.count(),
#             })
#         return JsonResponse(jobs_data, safe=False)
#     elif request.method == "POST":
#         try:
#             data = json.loads(request.body)
#         except json.JSONDecodeError:
#             return JsonResponse({'error': 'Invalid JSON'}, status=400)
#         required_fields = ['title', 'client_email', 'over_all_income']
#         missing_fields = [field for field in required_fields if field not in data or not data[field]]
#         if missing_fields:
#             return JsonResponse({'error': f"Missing: {', '.join(missing_fields)}"}, status=400)
#         try:
#             over_all_income = float(data['over_all_income'])
#         except ValueError:
#             return JsonResponse({'error': 'over_all_income must be a number'}, status=400)
#         job = CrmJob.objects.create(
#             client_email=data['client_email'],
#             full_name=data.get('full_name', ''),
#             phone_number=data.get('phone_number', ''),
#             position=data.get('position', ''),
#             client_company_name=data.get('client_company_name', ''),
#             client_company_phone=data.get('client_company_phone', ''),
#             client_company_address=data.get('client_company_address', ''),
#             client_website=data.get('client_website', ''),
#             status=data.get('status', 'active'),  # добавлено поле status
#         )
#         job_data = {
#             'id': job.id,
#             'client_email': job.client_email,
#             'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
#             'full_name': job.full_name,
#             'phone_number': job.phone_number,
#             'position': job.position,
#             'client_company_name': job.client_company_name,
#             'client_company_phone': job.client_company_phone,
#             'client_company_address': job.client_company_address,
#             'client_website': job.client_website,
#             'project_count': job.crm_tasks.count(),
#             'task_count': job.crm_tasks.count(),
#         }
#         return JsonResponse(job_data, status=201)
#
# @csrf_exempt
# @require_http_methods(["GET"])
# def api_get_job_detail(request, job_id):
#     job = get_object_or_404(CrmJob, id=job_id)
#     job_data = {
#         'id': job.id,
#         'client_email': job.client_email,
#         'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
#         'full_name': job.full_name,
#         'phone_number': job.phone_number,
#         'position': job.position,
#         'client_company_name': job.client_company_name,
#         'client_company_phone': job.client_company_phone,
#         'client_company_address': job.client_company_address,
#         'client_website': job.client_website,
#         'project_count': job.crm_tasks.count(),
#         'task_count': job.crm_tasks.count(),
#     }
#     return JsonResponse(job_data)
#
# @csrf_exempt
# @require_http_methods(["PUT", "PATCH"])
# def api_update_job(request, job_id):
#     job = get_object_or_404(CrmJob, id=job_id)
#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({'error': 'Invalid JSON'}, status=400)
#     for field in [ 'client_email', 'full_name', 'phone_number', 'position', 'client_company_name', 'client_company_phone', 'client_company_address', 'client_website']:
#         if field in data:
#             setattr(job, field, data[field])
#
#
#     job.save()
#     job_data = {
#         'id': job.id,
#         'client_email': job.client_email,
#         'created_at': job.created_at.isoformat() if hasattr(job, 'created_at') and job.created_at else None,
#         'full_name': job.full_name,
#         'phone_number': job.phone_number,
#         'position': job.position,
#         'client_company_name': job.client_company_name,
#         'client_company_phone': job.client_company_phone,
#         'client_company_address': job.client_company_address,
#         'client_website': job.client_website,
#         'project_count': job.crm_tasks.count(),
#         'task_count': job.crm_tasks.count(),
#     }
#     return JsonResponse(job_data)
#
# @csrf_exempt
# @require_http_methods(["DELETE"])
# def api_delete_job(request, job_id):
#     job = get_object_or_404(CrmJob, id=job_id)
#     job.delete()
#     return HttpResponse(status=204)


#new version with speed up

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Sum, Count, Prefetch
from django.utils.dateparse import parse_date
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import json

from .models_crm import CrmJob

# Cached field list for reuse
JOB_FIELDS = [
    'id', 'client_email', 'created_at', 'full_name', 'phone_number',
    'position', 'client_company_name', 'client_company_phone',
    'client_company_address', 'client_website'
]


def serialize_job(job, task_count=None):
    """Fast job serialization with optional task count"""
    return {
        'id': job.id,
        'client_email': job.client_email,
        'created_at': job.created_at.isoformat() if job.created_at else None,
        'full_name': job.full_name,
        'phone_number': job.phone_number,
        'position': job.position,
        'client_company_name': job.client_company_name,
        'client_company_phone': job.client_company_phone,
        'client_company_address': job.client_company_address,
        'client_website': job.client_website,
        'project_count': task_count if task_count is not None else 0,
        'task_count': task_count if task_count is not None else 0,
    }


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_get_all_jobs(request):
    if request.method == "GET":
        # Major optimization: Use annotate to get task counts in single query
        jobs = CrmJob.objects.select_related().annotate(
            task_count=Count('crm_tasks')
        ).only(*JOB_FIELDS)

        # Fast list comprehension instead of loop
        jobs_data = [
            serialize_job(job, job.task_count) for job in jobs
        ]

        return JsonResponse(jobs_data, safe=False)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # More efficient validation
        required_fields = {'title', 'client_email', 'over_all_income'}
        provided_fields = set(data.keys())
        missing_fields = required_fields - provided_fields

        if missing_fields:
            return JsonResponse({
                'error': f"Missing: {', '.join(missing_fields)}"
            }, status=400)

        # Validate numeric field upfront
        try:
            over_all_income = float(data['over_all_income'])
        except (ValueError, TypeError):
            return JsonResponse({
                'error': 'over_all_income must be a number'
            }, status=400)

        # Bulk field assignment using dictionary comprehension
        job_fields = {
            field: data.get(field, '')
            for field in ['client_email', 'full_name', 'phone_number', 'position',
                          'client_company_name', 'client_company_phone',
                          'client_company_address', 'client_website']
            if field in data
        }
        job_fields['status'] = data.get('status', 'active')

        job = CrmJob.objects.create(**job_fields)

        return JsonResponse(serialize_job(job), status=201)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_job_detail(request, job_id):
    # Optimize single job query with select_related and annotate
    job = get_object_or_404(
        CrmJob.objects.select_related().annotate(
            task_count=Count('crm_tasks')
        ).only(*JOB_FIELDS),
        id=job_id
    )

    return JsonResponse(serialize_job(job, job.task_count))


@csrf_exempt
@require_http_methods(["PUT", "PATCH"])
def api_update_job(request, job_id):
    job = get_object_or_404(CrmJob, id=job_id)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # Batch field updates
    update_fields = []
    allowed_fields = {
        'client_email', 'full_name', 'phone_number', 'position',
        'client_company_name', 'client_company_phone',
        'client_company_address', 'client_website', 'status'
    }

    for field in allowed_fields:
        if field in data:
            setattr(job, field, data[field])
            update_fields.append(field)

    # Only save if there are actual changes
    if update_fields:
        job.save(update_fields=update_fields)

    # Get task count efficiently
    task_count = job.crm_tasks.count()

    return JsonResponse(serialize_job(job, task_count))


@csrf_exempt
@require_http_methods(["DELETE"])
def api_delete_job(request, job_id):
    # Use bulk delete for better performance
    deleted_count, _ = CrmJob.objects.filter(id=job_id).delete()

    if deleted_count == 0:
        return JsonResponse({'error': 'Job not found'}, status=404)

    return HttpResponse(status=204)


# Additional optimization: Bulk operations endpoint
@csrf_exempt
@require_http_methods(["POST"])
def api_bulk_jobs(request):
    """Handle bulk job operations for maximum efficiency"""
    try:
        data = json.loads(request.body)
        action = data.get('action')
        job_ids = data.get('job_ids', [])

        if action == 'delete':
            deleted_count, _ = CrmJob.objects.filter(id__in=job_ids).delete()
            return JsonResponse({'deleted_count': deleted_count})

        elif action == 'update':
            update_data = data.get('update_data', {})
            updated_count = CrmJob.objects.filter(id__in=job_ids).update(**update_data)
            return JsonResponse({'updated_count': updated_count})

        else:
            return JsonResponse({'error': 'Invalid action'}, status=400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
