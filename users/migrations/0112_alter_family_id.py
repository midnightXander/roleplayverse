# Generated by Django 4.2.7 on 2024-09-14 20:08

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0111_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('1dda29c5-8d21-44c7-bc4c-e677cfc3213d'), primary_key=True, serialize=False),
        ),
    ]