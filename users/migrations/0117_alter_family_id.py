# Generated by Django 4.2.7 on 2024-09-16 13:35

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0116_remove_playernotification_battle_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('905ac904-d3ed-4a9b-95f5-169b5bc2dece'), primary_key=True, serialize=False),
        ),
    ]
