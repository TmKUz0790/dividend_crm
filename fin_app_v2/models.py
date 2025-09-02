

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 

class Job(models.Model):
    title = models.CharField(max_length=100)
    client_email = models.EmailField(unique=True)
    client_password = models.CharField(max_length=100)
    over_all_income = models.PositiveIntegerField(default=0)  # Total income for the job
    created_at = models.DateTimeField(auto_now_add=True, null=True)  # Add this field
    def __str__(self):
        return self.title

    def get_overall_progress(self):
        total_percentage = 0
        total_weight = 0

        # Используйте related_name для получения всех задач, связанных с объектом
        tasks = self.tasks.all()  # если related_name не задан, используйте _set

        for task in tasks:
            total_percentage += task.progress * (task.task_percentage / 100)
            total_weight += task.task_percentage

        if total_weight > 0:
            overall_progress = (total_percentage / total_weight) * 100
        else:
            overall_progress = 0

           


        return round(overall_progress)

# Добавьте в модель Task в models.py

class Task(models.Model):
    TASK_TYPE_CHOICES = [
        ('Обычная', 'Обычная'),
        ('Подписка', 'Подписка')
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=100)
    hours = models.PositiveIntegerField(default=1)
    description = models.TextField()
    assigned_users = models.ManyToManyField(User, related_name='developer_tasks')
    task_percentage = models.PositiveIntegerField()
    progress = models.PositiveIntegerField(default=0)
    start_date = models.DateField(auto_now_add=True, null=True)
    deadline = models.DateField(null=True, blank=True)
    feedback = models.TextField(blank=True, null=True)
    money_for_task = models.PositiveIntegerField(default=0)
    paid = models.BooleanField(default=False)
    assigned_email = models.EmailField(blank=True, null=True)
    task_type = models.CharField(
        max_length=10,
        choices=TASK_TYPE_CHOICES,
        default='Обычная'
    )
    task_status = models.CharField(
        max_length=20,
        default='Бошланмади',
        choices=[
            ('Бошланмади', 'Бошланмади'),
            ('Иш бошланди', 'Иш бошланди'),
            ('Текширишда', 'Текширишда'),
            ('Топшириш жараёнида ', 'Топшириш жараёнида '),
            ('Ёпилди', 'Ёпилди'),    
        ]
    )
    # Новые поля для подтверждения задач
    confirmed = models.BooleanField(default=False)
    confirmation_date = models.DateTimeField(null=True, blank=True)
    confirmed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='confirmed_tasks'
    )

    def __str__(self):
        return self.title

    def check_and_pay_developer(self):
        # Оплата производится только после подтверждения администратором
        if self.progress == 100 and self.confirmed and not self.paid:
            self.paid = True
            self.save()

from django.db import models
from django.contrib.auth.models import User

class DeductionLog(models.Model):
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deductions')
    deducted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deduction_actions')  # Admin who deducted
    deduction_amount = models.PositiveIntegerField()
    deduction_date = models.DateTimeField(auto_now_add=True)  # Automatically logs the date and time of deduction

    def __str__(self):
        return f"{self.deducted_by.username} deducted {self.deduction_amount} USD from {self.developer.username} on {self.deduction_date}"

from django.db.models import Sum

def calculate_income_balance():
    # Sum all money_for_task from Task model
    total_task_money = Task.objects.aggregate(Sum('money_for_task'))['money_for_task__sum'] or 0

    # Sum all over_all_income from Job model
    total_job_income = Job.objects.aggregate(Sum('over_all_income'))['over_all_income__sum'] or 0

    # Calculate the remaining balance
    income_balance = total_job_income - total_task_money

    return {
        "total_task_money": total_task_money,
        "total_job_income": total_job_income,
        "income_balance": income_balance,
    }


# Add this to your models.py file

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
import calendar


# Add this method to your Task model
def create_monthly_recurring_tasks(self):
    """Create recurring monthly tasks for a year if task type is PATPIS (Follow Task)"""
    if self.task_type == 'Подписка':
        # Get today's date
        today = timezone.now().date()
        # Get the base task name (without month name)
        base_title = self.title

        # Create tasks for the next 12 months (including current month)
        for i in range(12):
            # Calculate target month's date
            target_date = today.replace(day=1) + timedelta(days=32 * i)
            target_date = target_date.replace(
                day=min(today.day, calendar.monthrange(target_date.year, target_date.month)[1]))

            # Get month name
            month_name = target_date.strftime('%B')

            # Skip creating duplicate for current month as the current task serves for it
            if i == 0:
                # Update current task's title to include current month
                self.title = f"{base_title} ({month_name})"
                self.save()
                continue

            # Create a new task for each future month
            new_task = Task(
                job=self.job,
                title=f"{base_title} ({month_name})",
                hours=self.hours,
                description=self.description,
                task_percentage=self.task_percentage,
                money_for_task=self.money_for_task,
                task_type='Подписка',
                deadline=target_date  # Set deadline to the same day in the target month
            )
            new_task.save()

            # Copy assigned users
            for user in self.assigned_users.all():
                new_task.assigned_users.add(user)



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
        try:
            return round(self.file.size / (1024 * 1024), 2) if self.file else 0
        except Exception:
            return 0

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