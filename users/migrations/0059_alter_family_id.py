# Generated by Django 4.2.7 on 2024-07-17 10:02

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0058_player_profile_picture_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('46d9185a-9d34-4961-998d-e4d63096bba8'), primary_key=True, serialize=False),
        ),
    ]