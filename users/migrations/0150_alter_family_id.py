# Generated by Django 4.2.7 on 2024-10-05 09:00

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0149_rename_referall_link_player_referall_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='family',
            name='id',
            field=models.UUIDField(default=uuid.UUID('f2adc55e-6fed-4366-9b39-609a21c3577f'), primary_key=True, serialize=False),
        ),
    ]
