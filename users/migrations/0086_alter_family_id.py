# Generated by Django 4.2.7 on 2024-08-29 07:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0085_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('e69142a1-2bee-41c8-a7b8-24067ccce3d6'), primary_key=True, serialize=False),
        ),
    ]
