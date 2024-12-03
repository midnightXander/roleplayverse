# Generated by Django 4.2.7 on 2024-07-17 08:07

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0057_alter_family_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='profile_picture',
            field=models.ImageField(default='blank-profile-picture.png', upload_to='players/profile_pics/'),
        ),
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('34d54043-2e5b-4d94-9289-a5502908b0a4'), primary_key=True, serialize=False),
        ),
    ]