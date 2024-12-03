# Generated by Django 4.2.7 on 2024-07-05 19:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0029_alter_family_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='language',
            field=models.CharField(default='en', max_length=20),
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('48bfe2dd-381c-4910-a621-125b6675a94f'), primary_key=True, serialize=False),
        ),
    ]
