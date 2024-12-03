# Generated by Django 4.2.7 on 2024-06-23 00:09

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0012_alter_family_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('receiver', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='message_receiver', to='users.player')),
                ('sender', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.player')),
            ],
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.UUIDField(default=uuid.UUID('3b075074-f301-401e-99f1-900b4cd78fde'), primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
    ]
