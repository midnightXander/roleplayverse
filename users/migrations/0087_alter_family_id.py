# Generated by Django 4.2.7 on 2024-08-31 08:39

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0086_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f4c6037c-f8b2-4788-9a0b-a24304d67eb4'), primary_key=True, serialize=False),
        ),
    ]
