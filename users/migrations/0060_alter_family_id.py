# Generated by Django 4.2.7 on 2024-07-17 10:22

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0059_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('9882023f-0db1-49d5-8833-4c3716a7a982'), primary_key=True, serialize=False),
        ),
    ]
