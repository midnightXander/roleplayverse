# Generated by Django 4.2.7 on 2024-07-01 21:12

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0009_alter_chat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='id',
            field=models.UUIDField(default=uuid.UUID('bf839352-91e9-475d-b58a-410e079ae129'), primary_key=True, serialize=False),
        ),
    ]