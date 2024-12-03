# Generated by Django 4.2.7 on 2024-10-01 10:33

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0143_player_date_joined_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('74d3a87e-4849-4acf-8dc9-261d075006b5'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='player',
            name='date_joined',
            field=models.DateField(auto_now_add=True),
        ),
    ]