from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("fin_app_v2", "0026_add_task_id_to_applicationtaskcompletion"),
    ]
    operations = [
        migrations.AddField(
            model_name="applicationtaskcompletion",
            name="status",
            field=models.CharField(
                max_length=32,
                choices=[
                    ("new", "Новая"),
                    ("in_progress", "В работе"),
                    ("done", "Завершена"),
                ],
                default="new",
                verbose_name="Статус задачи",
            ),
        ),
    ]
