# Generated by Django 4.2.7 on 2024-07-18 12:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0062_player_bio_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('c5347ad9-3f27-4706-b008-d82d56f00785'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='bio',
            field=models.CharField(blank=True, max_length=60),
        ),
    ]