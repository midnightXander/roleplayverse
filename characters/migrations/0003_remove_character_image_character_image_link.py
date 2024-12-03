# Generated by Django 4.2.7 on 2024-07-05 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters', '0002_alter_character_jutsu'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='character',
            name='image',
        ),
        migrations.AddField(
            model_name='character',
            name='image_link',
            field=models.TextField(default='https://static.wikia.nocookie.net/naruto/images/e/e6/Ten-Tails_emerges.png'),
        ),
    ]