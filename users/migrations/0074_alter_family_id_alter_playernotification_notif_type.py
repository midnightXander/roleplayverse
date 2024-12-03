# Generated by Django 4.2.7 on 2024-07-25 17:32

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0073_remove_family_bio_family_description_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('4865a63c-0e5a-4c4e-b16d-d54c6739f58a'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='playernotification',
            name='notif_type',
            field=models.CharField(choices=[('invite', 'invite'), ('request', 'request'), ('private_message', 'private_message'), ('textpad', 'textpad'), ('family_message', 'family_message'), ('refused_request', 'refused_request'), ('denied_invite', 'denied_invite'), ('battle_accepted', 'battle_accepted'), ('refree_proposal', 'refree_proposal')], max_length=30),
        ),
    ]