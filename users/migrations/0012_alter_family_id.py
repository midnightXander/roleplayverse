# Generated by Django 4.2.7 on 2024-06-23 00:09

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c458df12-bca8-43e5-8aae-d3c270192a50'), primary_key=True, serialize=False),
        ),
    ]
