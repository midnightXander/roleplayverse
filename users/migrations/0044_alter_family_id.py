# Generated by Django 4.2.7 on 2024-07-11 21:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0043_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('330e0f8f-7df3-45ab-960d-7fc0786b2ced'), primary_key=True, serialize=False),
        ),
    ]
