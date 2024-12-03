# Generated by Django 4.2.7 on 2024-10-06 10:29

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0150_alter_family_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='last_seen',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('a1081e0c-6d61-4f09-b30d-a5e57002165f'), primary_key=True, serialize=False),
        ),
    ]