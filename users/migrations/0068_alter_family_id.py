# Generated by Django 4.2.7 on 2024-07-21 22:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0067_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('2e42fed3-417b-4670-867e-562ae50a177d'), primary_key=True, serialize=False),
        ),
    ]