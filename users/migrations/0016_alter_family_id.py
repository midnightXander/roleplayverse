# Generated by Django 4.2.7 on 2024-06-26 19:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('76c3fd06-b3a5-4b51-ab8b-35d764f7419e'), primary_key=True, serialize=False),
        ),
    ]