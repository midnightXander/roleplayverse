# Generated by Django 4.2.7 on 2024-07-11 14:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0037_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('d2d9f353-5262-4425-bb4d-c9cacaac4c63'), primary_key=True, serialize=False),
        ),
    ]
