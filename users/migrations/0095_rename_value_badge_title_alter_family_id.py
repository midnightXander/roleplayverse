# Generated by Django 4.2.7 on 2024-09-08 18:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0094_badge_remove_player_flags_alter_family_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='badge',
            old_name='value',
            new_name='title',
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('55a56d8f-3ce8-4f43-90f3-1054c9fb599d'), primary_key=True, serialize=False),
        ),
    ]
