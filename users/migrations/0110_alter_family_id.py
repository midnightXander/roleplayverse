# Generated by Django 4.2.7 on 2024-09-13 19:21

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0109_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('29dc1992-4169-4154-b988-06dc23b91d80'), primary_key=True, serialize=False),
        ),
    ]