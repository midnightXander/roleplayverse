# Generated by Django 4.2.7 on 2024-07-05 09:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0024_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('2e95b270-b582-4090-91aa-8539155cad3b'), primary_key=True, serialize=False),
        ),
    ]