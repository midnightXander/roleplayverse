# Generated by Django 4.2.7 on 2024-12-10 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_alter_player_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='country',
            field=models.CharField(max_length=80),
        ),
        migrations.AlterField(
            model_name='player',
            name='language',
            field=models.CharField(default='fr', max_length=20),
        ),
    ]
