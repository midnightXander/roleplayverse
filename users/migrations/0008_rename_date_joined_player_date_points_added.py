# Generated by Django 4.2.7 on 2024-12-17 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_player_country_alter_player_language'),
    ]

    operations = [
        migrations.RenameField(
            model_name='player',
            old_name='date_joined',
            new_name='date_points_added',
        ),
    ]
