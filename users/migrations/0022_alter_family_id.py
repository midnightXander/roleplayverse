# Generated by Django 4.2.7 on 2024-07-04 18:23

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('ae52e30e-66ff-4789-896b-d5d632e341ea'), primary_key=True, serialize=False),
        ),
    ]