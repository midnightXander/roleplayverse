# Generated by Django 4.2.7 on 2024-07-13 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0015_battle_refreeing_rating_refree'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='can_send_textpad',
            field=models.BooleanField(default=False),
        ),
    ]
