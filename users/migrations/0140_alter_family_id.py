# Generated by Django 4.2.7 on 2024-09-29 16:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0139_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('872ce34e-1918-4c45-b363-f15f14d79b98'), primary_key=True, serialize=False),
        ),
    ]