# Generated by Django 4.2.7 on 2024-09-13 11:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_alter_fightertournament_round'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='tournaments/covers/7.jpg', upload_to=''),
        ),
    ]
