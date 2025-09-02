from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ("fin_app_v2", "0027_add_status_to_applicationtaskcompletion"),
    ]
    operations = [
        migrations.AddField(
            model_name="applicationtaskcompletion",
            name="task_id",
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
