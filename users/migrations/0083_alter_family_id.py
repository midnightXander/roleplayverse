# Generated by Django 4.2.7 on 2024-08-27 23:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0082_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ba1eea86-38c9-46f3-a6a1-26e5aa5c27a2'), primary_key=True, serialize=False),
        ),
    ]