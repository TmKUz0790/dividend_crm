
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

class Lead(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100, blank=True)
    varonka = models.ForeignKey(Varonka, on_delete=models.SET_NULL, null=True)
    current_task = models.ForeignKey(VaronkaTask, on_delete=models.SET_NULL, null=True, blank=True)
    is_done = models.BooleanField(default=False)

    def __str__(self):
        return self.name
