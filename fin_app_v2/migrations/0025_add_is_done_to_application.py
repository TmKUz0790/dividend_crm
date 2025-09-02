from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('fin_app_v2', '0024_add_status_to_application'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
    ]
