# Generated by Django 4.2.7 on 2024-07-12 13:59

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0048_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('00f47e3c-2420-4c72-96fa-5e2550376c31'), primary_key=True, serialize=False),
        ),
    ]
