
from django.db import models

class Varonka(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class VaronkaTask(models.Model):
    varonka = models.ForeignKey(Varonka, related_name='tasks', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.varonka.name} - {self.name}"


# Универсальная заявка/карточка для канбана
class Application(models.Model):
    STAGE_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("done", "Завершена"),
    ]
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    stage = models.CharField(max_length=32, choices=STAGE_CHOICES, default="new")
    is_done = models.BooleanField(default=False, verbose_name='Статус')

    def __str__(self):
        return self.name
