#
# from django.db import models
#
# class Varonka(models.Model):
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#
#     def __str__(self):
#         return self.name
#
# class VaronkaTask(models.Model):
#     varonka = models.ForeignKey(Varonka, related_name='tasks', on_delete=models.CASCADE)
#     name = models.CharField(max_length=100)
#     order = models.PositiveIntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.varonka.name} - {self.name}"
#
#
# # Универсальная заявка/карточка для канбана
# class Application(models.Model):
#     STAGE_CHOICES = [
#         ("new", "Новая"),
#         ("in_progress", "В работе"),
#         ("done", "Завершена"),
#     ]
#     name = models.CharField(max_length=100)
#     contact = models.CharField(max_length=100, blank=True)
#     stage = models.CharField(max_length=32, choices=STAGE_CHOICES, default="new")
#     is_done = models.BooleanField(default=False, verbose_name='Статус')
#
#     def __str__(self):
#         return self.name

from django.db import models


class Varonka(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class VaronkaTask(models.Model):
    varonka = models.ForeignKey(Varonka, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, help_text="Detailed description of what this task involves")
    is_required = models.BooleanField(default=True, help_text="Is this task mandatory?")

    class Meta:
        ordering = ['order']
        unique_together = ['varonka', 'order']  # Ensure unique ordering within each varonka

    def __str__(self):
        return f"{self.varonka.name} - {self.name}"


# Universal application/card for kanban
class Application(models.Model):
    STAGE_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("done", "Завершена"),
    ]

    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    stage = models.CharField(max_length=32, choices=STAGE_CHOICES, default="new")
    status = models.CharField(max_length=32, choices=STAGE_CHOICES, default="new", verbose_name='Статус')
    is_done = models.BooleanField(default=False)

    # Link to varonka for structured workflow
    varonka = models.ForeignKey(Varonka, on_delete=models.CASCADE, null=True, blank=True)
    current_task = models.ForeignKey(VaronkaTask, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_next_task(self):
        """Get the next task in the varonka sequence"""
        if not self.varonka:
            return None

        completed_tasks = self.task_completions.values_list('task_id', flat=True)
        next_task = self.varonka.tasks.exclude(id__in=completed_tasks).order_by('order').first()
        return next_task

    def progress_percentage(self):
        """Calculate completion percentage based on completed tasks"""
        if not self.varonka:
            return 0

        total_tasks = self.varonka.tasks.count()
        if total_tasks == 0:
            return 0

        completed_tasks = self.task_completions.count()
        return int((completed_tasks / total_tasks) * 100)


# Track task completion for each application
class ApplicationTaskCompletion(models.Model):
    application = models.ForeignKey(Application, related_name='task_completions', on_delete=models.CASCADE)
    task = models.ForeignKey(VaronkaTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, help_text="Notes about task completion")
    completed_by = models.CharField(max_length=100, blank=True)  # Could be ForeignKey to User model

    class Meta:
        unique_together = ['application', 'task']  # Prevent duplicate completions

    def __str__(self):
        return f"{self.application.name} - {self.task.name} (Completed)"


# Optional: Template system for creating varonkas with predefined tasks
class VaronkaTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Template: {self.name}"

    def create_varonka(self, varonka_name):
        """Create a new varonka from this template"""
        varonka = Varonka.objects.create(
            name=varonka_name,
            description=self.description
        )

        # Copy tasks from template
        for template_task in self.template_tasks.all():
            VaronkaTask.objects.create(
                varonka=varonka,
                name=template_task.name,
                order=template_task.order,
                description=template_task.description,
                is_required=template_task.is_required
            )

        return varonka


class VaronkaTemplateTask(models.Model):
    template = models.ForeignKey(VaronkaTemplate, related_name='template_tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.template.name} - {self.name}"
