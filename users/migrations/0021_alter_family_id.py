# Generated by Django 4.2.7 on 2024-07-01 21:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_playernotification_read_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('06b4be7d-601e-4672-8de6-a72c3440bd44'), primary_key=True, serialize=False),
        ),
    ]
