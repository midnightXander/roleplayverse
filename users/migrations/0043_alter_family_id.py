# Generated by Django 4.2.7 on 2024-07-11 20:52

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0042_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('21e6332b-df75-4ffd-9173-de3cc77aef43'), primary_key=True, serialize=False),
        ),
    ]