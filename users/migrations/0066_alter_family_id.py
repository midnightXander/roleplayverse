# Generated by Django 4.2.7 on 2024-07-20 19:38

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0065_alter_family_id_alter_playernotification_notif_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c9f6cbff-23b0-449d-8851-9a346d340678'), primary_key=True, serialize=False),
        ),
    ]
