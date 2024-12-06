# Generated by Django 4.2.7 on 2024-12-06 15:42

from django.db import migrations, models
import events.models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_tournament_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='tournaments/covers/1.png', upload_to=events.models.tournament_upload_to),
        ),
    ]
