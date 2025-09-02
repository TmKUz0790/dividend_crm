from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fin_app_v2', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='status',
            field=models.CharField(
                max_length=32,
                choices=[('new', 'Новая'), ('in_progress', 'В работе'), ('done', 'Завершена')],
                default='new',
                verbose_name='Статус',
            ),
        ),
    ]
