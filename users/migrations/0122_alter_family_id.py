# Generated by Django 4.2.7 on 2024-09-18 18:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0121_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('dad44ecb-3cc2-4c74-b113-c28ace7c3901'), primary_key=True, serialize=False),
        ),
    ]
