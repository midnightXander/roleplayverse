# Generated by Django 4.2.7 on 2024-07-12 15:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0050_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('37958ed5-4dbb-46ec-8227-c4de611937cb'), primary_key=True, serialize=False),
        ),
    ]
