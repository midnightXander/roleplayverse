# Generated by Django 4.2.7 on 2024-06-21 13:08

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('20fdfaf6-f736-47c6-9d63-b3c996075d5f'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='family',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.family'),
        ),
    ]
