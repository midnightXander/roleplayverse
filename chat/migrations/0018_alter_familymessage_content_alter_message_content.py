# Generated by Django 4.2.7 on 2024-09-16 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0017_alter_familymessage_content_alter_message_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='familymessage',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='message',
            name='content',
            field=models.TextField(blank=True, null=True),
        ),
    ]