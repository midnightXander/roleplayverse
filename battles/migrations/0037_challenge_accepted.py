# Generated by Django 4.2.7 on 2024-09-20 17:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0036_challenge'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='accepted',
            field=models.BooleanField(default=False),
        ),
    ]