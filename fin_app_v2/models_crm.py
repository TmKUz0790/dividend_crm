from django.db import models

class CrmJob(models.Model):
    # Основные поля
    client_email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Новые поля по ТЗ
    full_name = models.CharField("ФИО", max_length=255, blank=True, default="")
    phone_number = models.CharField("Номер телефона", max_length=32, blank=True, default="")
    position = models.CharField("Позиция", max_length=32, choices=[('Менеджер', 'Менеджер'), ('Директор', 'Директор')], blank=True, default="")
    client_company_name = models.CharField("Название клиентской компании", max_length=255, blank=True, default="")
    client_company_phone = models.CharField("Номер телефона клиентской компании", max_length=32, blank=True, default="")
    client_company_address = models.CharField("Адрес клиентской компании", max_length=255, blank=True, default="")
    client_website = models.CharField("Адрес веб-сайта", max_length=255, blank=True, default="")
    
    STATUS_CHOICES = [
        ("active", "Активен"),
        ("inactive", "Неактивен"),
    ]
    status = models.CharField("Статус", max_length=8, choices=STATUS_CHOICES, default="active")

    def __str__(self):
        return self.title

# Для задач и комментариев/файлов можно добавить аналогично:
class CrmTask(models.Model):
    job = models.ForeignKey(CrmJob, on_delete=models.CASCADE, related_name='crm_tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    # ... другие поля задачи ...

class CrmTaskComment(models.Model):
    task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_comments')
    author = models.CharField(max_length=255)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class CrmTaskFile(models.Model):
    task = models.ForeignKey(CrmTask, on_delete=models.CASCADE, related_name='crm_files')
    file = models.FileField(upload_to='task_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
