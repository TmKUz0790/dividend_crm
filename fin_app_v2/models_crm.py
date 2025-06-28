# from django.db import models
#
# class CrmJob(models.Model):
#     # Основные поля
#     client_email = models.EmailField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     # Новые поля по ТЗ
#     full_name = models.CharField("ФИО", max_length=255, blank=True, default="")
#     phone_number = models.CharField("Номер телефона", max_length=32, blank=True, default="")
#     position = models.CharField("Позиция", max_length=32, choices=[('Менеджер', 'Менеджер'), ('Директор', 'Директор')], blank=True, default="")
#     client_company_name = models.CharField("Название клиентской компании", max_length=255, blank=True, default="")
#     client_company_phone = models.CharField("Номер телефона клиентской компании", max_length=32, blank=True, default="")
#     client_company_address = models.CharField("Адрес клиентской компании", max_length=255, blank=True, default="")
#     client_website = models.CharField("Адрес веб-сайта", max_length=255, blank=True, default="")
#
#     STATUS_CHOICES = [
#         ("АКБ", "АКБ"),
#         ("ОКБ", "ОКБ"),
#     ]
#     status = models.CharField("Статус", max_length=8, choices=STATUS_CHOICES, default="active")
#
#     def __str__(self):
#         return self.title
#
# class CrmTask(models.Model):
#     TASK_TYPE_CHOICES = [
#         ("SIMPLE", "Обычная"),
#         ("FEEDBACK", "Обратная связь"),
#         ("MEETING", "Встреча"),
#     ]
#
#     job = models.ForeignKey(CrmJob, on_delete=models.CASCADE, related_name='crm_tasks')
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, default="")
#
#     task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default="SIMPLE")
#     assigned_to = models.CharField(max_length=255, blank=True, default="")
#     subtasks = models.JSONField(blank=True, default=list)
#
#
# class CrmTaskComment(models.Model):
#     task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_comments')
#     author = models.CharField(max_length=255)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
# class CrmTaskFile(models.Model):
#     task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_files')
#     file = models.FileField(upload_to='task_files/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#######################################################################################################################
#
# # models_crm.py - UPDATE YOUR EXISTING FILE
#
# from django.db import models
# from .models import Job  # Import your existing Job model
#
#
# class CrmJob(models.Model):
#     # Основные поля
#     client_email = models.EmailField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     # ADD THIS NEW FIELD - Link to existing Job
#     existing_job = models.ForeignKey(
#         Job,
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='crm_jobs',
#         verbose_name="Связанная работа"
#     )
#
#     # Новые поля по ТЗ
#     full_name = models.CharField("ФИО", max_length=255, blank=True, default="")
#     phone_number = models.CharField("Номер телефона", max_length=32, blank=True, default="")
#     position = models.CharField("Позиция", max_length=32, choices=[('Менеджер', 'Менеджер'), ('Директор', 'Директор')],
#                                 blank=True, default="")
#     client_company_name = models.CharField("Название клиентской компании", max_length=255, blank=True, default="")
#     client_company_phone = models.CharField("Номер телефона клиентской компании", max_length=32, blank=True, default="")
#     client_company_address = models.CharField("Адрес клиентской компании", max_length=255, blank=True, default="")
#     client_website = models.CharField("Адрес веб-сайта", max_length=255, blank=True, default="")
#
#     STATUS_CHOICES = [
#         ("АКБ", "АКБ"),
#         ("ОКБ", "ОКБ"),
#     ]
#     status = models.CharField("Статус", max_length=8, choices=STATUS_CHOICES, default="АКБ")
#
#     def __str__(self):
#         if self.full_name:
#             return f"{self.full_name} - {self.client_company_name}"
#         return self.client_email
#
#     # Auto-populate fields from linked job
#     def save(self, *args, **kwargs):
#         if self.existing_job:
#             # Auto-fill from linked job if fields are empty
#             if not self.client_email:
#                 self.client_email = self.existing_job.client_email
#             if not self.client_company_name:
#                 self.client_company_name = self.existing_job.title
#         super().save(*args, **kwargs)
#
#
# class CrmTask(models.Model):
#     TASK_TYPE_CHOICES = [
#         ("SIMPLE", "Обычная"),
#         ("FEEDBACK", "Обратная связь"),
#         ("MEETING", "Встреча"),
#     ]
#
#     job = models.ForeignKey(CrmJob, on_delete=models.CASCADE, related_name='crm_tasks')
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, default="")
#
#     task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default="SIMPLE")
#     assigned_to = models.CharField(max_length=255, blank=True, default="")
#     subtasks = models.JSONField(blank=True, default=list)
#
#     def __str__(self):
#         return self.title
#
#
# class CrmTaskComment(models.Model):
#     task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_comments')
#     author = models.CharField(max_length=255)
#     text = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"Comment by {self.author} on {self.task.title}"
#
#
# class CrmTaskFile(models.Model):
#     task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_files')
#     file = models.FileField(upload_to='task_files/')
#     uploaded_at = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"File for {self.task.title}"


# models_crm.py - COMPLETE FILE

import os
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from .models import Job  # Import your existing Job model


# File validation functions
def validate_file_size(value):
    """Limit file size to 100MB"""
    filesize = value.size
    max_size = 100 * 1024 * 1024  # 100MB
    if filesize > max_size:
        raise ValidationError(f"File size cannot exceed 100MB. Current size: {filesize // (1024 * 1024)}MB")


def validate_file_type(value):
    """Block dangerous file types"""
    dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js']
    filename = value.name.lower()

    for ext in dangerous_extensions:
        if filename.endswith(ext):
            raise ValidationError(f"File type {ext} is not allowed for security reasons")


def crm_task_file_path(instance, filename):
    """Create organized path: crm_files/job_id/task_id/filename"""
    # Clean filename - remove special characters
    name, ext = os.path.splitext(filename)
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()

    # Limit filename length
    if len(safe_name) > 50:
        safe_name = safe_name[:50]

    safe_filename = f"{safe_name}{ext.lower()}"

    # Create organized path
    return f'crm_files/job_{instance.task.job.id}/task_{instance.task.id}/{safe_filename}'


class CrmJob(models.Model):
    # Основные поля
    client_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Link to existing Job
    existing_job = models.ForeignKey(
        Job,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='crm_jobs',
        verbose_name="Связанная работа"
    )

    # Новые поля по ТЗ
    full_name = models.CharField("ФИО", max_length=255, blank=True, default="")
    phone_number = models.CharField("Номер телефона", max_length=32, blank=True, default="")
    position = models.CharField("Позиция", max_length=32, choices=[('Менеджер', 'Менеджер'), ('Директор', 'Директор')],
                                blank=True, default="")
    client_company_name = models.CharField("Название клиентской компании", max_length=255, blank=True, default="")
    client_company_phone = models.CharField("Номер телефона клиентской компании", max_length=32, blank=True, default="")
    client_company_address = models.CharField("Адрес клиентской компании", max_length=255, blank=True, default="")
    client_website = models.CharField("Адрес веб-сайта", max_length=255, blank=True, default="")

    STATUS_CHOICES = [
        ("АКБ", "АКБ"),
        ("ОКБ", "ОКБ"),
    ]
    status = models.CharField("Статус", max_length=8, choices=STATUS_CHOICES, default="АКБ")

    def __str__(self):
        if self.full_name:
            return f"{self.full_name} - {self.client_company_name}"
        return self.client_email

    # Auto-populate fields from linked job
    def save(self, *args, **kwargs):
        if self.existing_job:
            # Auto-fill from linked job if fields are empty
            if not self.client_email:
                self.client_email = self.existing_job.client_email
            if not self.client_company_name:
                self.client_company_name = self.existing_job.title
        super().save(*args, **kwargs)


class CrmTask(models.Model):
    TASK_TYPE_CHOICES = [
        ("SIMPLE", "Обычная"),
        ("FEEDBACK", "Обратная связь"),
        ("MEETING", "Встреча"),
    ]

    job = models.ForeignKey(CrmJob, on_delete=models.CASCADE, related_name='crm_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default="SIMPLE")
    assigned_to = models.CharField(max_length=255, blank=True, default="")
    subtasks = models.JSONField(blank=True, default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']


class CrmTaskComment(models.Model):
    task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_comments')
    author = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.task.title}"

    class Meta:
        ordering = ['-created_at']


class CrmTaskFile(models.Model):
    task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_files')
    file = models.FileField(
        upload_to=crm_task_file_path,
        validators=[
            validate_file_size,
            validate_file_type,
            FileExtensionValidator(allowed_extensions=[
                'pdf', 'doc', 'docx', 'txt', 'csv',
                'xls', 'xlsx', 'jpg', 'jpeg', 'png', 'gif', 'webp',
                'zip', 'rar', 'ppt', 'pptx', 'mp4', 'avi', 'mov'
            ])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.CharField(max_length=255, blank=True, help_text="Email of uploader")

    def __str__(self):
        return f"File for {self.task.title}"

    @property
    def filename(self):
        """Get just the filename without path"""
        return os.path.basename(self.file.name)

    @property
    def file_size_mb(self):
        """Return file size in MB"""
        return round(self.file.size / (1024 * 1024), 2) if self.file else 0

    @property
    def file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.filename)[1].lower()

    @property
    def is_image(self):
        """Check if file is an image"""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return self.file_extension in image_extensions

    @property
    def is_document(self):
        """Check if file is a document"""
        doc_extensions = ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xls', '.xlsx', '.ppt', '.pptx']
        return self.file_extension in doc_extensions

    @property
    def is_video(self):
        """Check if file is a video"""
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv']
        return self.file_extension in video_extensions

    def delete(self, *args, **kwargs):
        """Delete actual file when model is deleted"""
        if self.file:
            try:
                if os.path.isfile(self.file.path):
                    os.remove(self.file.path)
            except:
                pass  # File might already be deleted or doesn't exist
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-uploaded_at']