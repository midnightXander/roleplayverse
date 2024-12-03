# Generated by Django 4.2.7 on 2024-07-24 00:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0071_family_profile_picture_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('799ba7e8-4d0d-4e59-a129-1b2494ff8810'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='playernotification',
            name='notif_type',
            field=models.CharField(choices=[('invite', 'invite'), ('request', 'request'), ('private_message', 'private_message'), ('textpad', 'textpad'), ('family_message', 'family_message'), ('refused_request', 'refused_request'), ('denied_invite', 'denied_invite')], max_length=30),
        ),
    ]
