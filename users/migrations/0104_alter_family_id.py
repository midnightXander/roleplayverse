# Generated by Django 4.2.7 on 2024-09-13 11:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0103_playernotification_battle_id_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c409b46f-0f2a-4329-9c30-cf9e20690b83'), primary_key=True, serialize=False),
        ),
    ]