# Generated by Django 4.2.7 on 2024-08-28 00:10

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0083_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('4957cc4d-bb88-4162-b846-55111fcc0d09'), primary_key=True, serialize=False),
        ),
    ]
