# Generated by Django 4.2.7 on 2024-09-16 11:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0020_alter_tournament_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='tournaments/covers/4.jpg', upload_to=''),
        ),
    ]
