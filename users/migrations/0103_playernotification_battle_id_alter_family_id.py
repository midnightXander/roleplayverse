# Generated by Django 4.2.7 on 2024-09-12 11:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0102_remove_playernotification_battle_id_alter_family_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='playernotification',
            name='battle_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('3838b604-4f2d-4d76-9941-fa8e3a55f3c4'), primary_key=True, serialize=False),
        ),
    ]