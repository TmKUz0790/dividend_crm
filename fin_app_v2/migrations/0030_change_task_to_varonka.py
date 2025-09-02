from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('fin_app_v2', '0029_merge_20250903_0014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicationtaskcompletion',
            name='task',
        ),
        migrations.AddField(
            model_name='applicationtaskcompletion',
            name='varonka',
            field=models.ForeignKey(to='fin_app_v2.varonka', on_delete=models.CASCADE, null=True),
        ),
    ]
