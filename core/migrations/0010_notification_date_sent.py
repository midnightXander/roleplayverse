# Generated by Django 4.2.7 on 2024-09-18 18:19

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_alter_notification_content_alter_notification_target_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='date_sent',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
