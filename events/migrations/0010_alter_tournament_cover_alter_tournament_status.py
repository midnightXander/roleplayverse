# Generated by Django 4.2.7 on 2024-09-13 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_tournament_cover'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='tournaments/covers/1.jpg', upload_to=''),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='status',
            field=models.CharField(choices=[('registering', 'registering'), ('not_started', 'not_started'), ('ongoing', 'ongoing'), ('finished', 'finished')], default='registering', max_length=20),
        ),
    ]
