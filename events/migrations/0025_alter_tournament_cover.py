# Generated by Django 4.2.7 on 2024-09-16 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0024_alter_tournament_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='tournaments/covers/5.jpg', upload_to=''),
        ),
    ]
