# Generated by Django 4.2.7 on 2024-10-22 14:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0156_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('22abcd60-865d-450d-8971-f8636db73cf5'), primary_key=True, serialize=False),
        ),
    ]
