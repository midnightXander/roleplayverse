# Generated by Django 4.2.7 on 2024-10-08 12:19

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0153_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a8282036-b4b8-43ea-a701-7f21c37badc4'), primary_key=True, serialize=False),
        ),
    ]