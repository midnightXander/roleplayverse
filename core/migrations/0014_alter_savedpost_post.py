# Generated by Django 4.2.7 on 2024-10-07 06:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_alter_post_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savedpost',
            name='post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='core.post'),
        ),
    ]
