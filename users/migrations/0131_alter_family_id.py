# Generated by Django 4.2.7 on 2024-09-21 00:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0130_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('9f664969-997a-4556-91c8-5300fb3dde9d'), primary_key=True, serialize=False),
        ),
    ]
