# Generated by Django 4.2.7 on 2024-07-17 10:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_post_reacted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='reacted',
        ),
    ]