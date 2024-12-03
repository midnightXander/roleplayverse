# Generated by Django 4.2.7 on 2024-10-04 01:15

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0148_alter_family_date_created_alter_family_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='referall_link',
            new_name='referall_code',
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c1c578fd-cc15-401a-add4-cad92edbb66c'), primary_key=True, serialize=False),
        ),
    ]