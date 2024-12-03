# Generated by Django 4.2.7 on 2024-06-27 21:09

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_chat_last_message_abbr_chat_last_message_time_sent_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('192806d8-3173-4f8f-902c-9db9930840f1'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='chat',
            name='last_message_abbr',
            field=models.TextField(),
        ),
    ]
