# Generated by Django 4.2.7 on 2024-07-13 18:44

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0053_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('540cf186-619f-4bdd-8404-8799a7b626e8'), primary_key=True, serialize=False),
        ),
    ]
