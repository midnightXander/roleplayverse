# Generated by Django 4.2.7 on 2024-07-11 21:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0007_alter_battle_date_ended'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='i_character',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.AddField(
            model_name='battle',
            name='o_character',
            field=models.CharField(blank=True, max_length=30),
        ),
    ]