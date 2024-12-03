# Generated by Django 4.2.7 on 2024-07-12 14:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0050_alter_family_id'),
        ('battles', '0012_alter_battle_refree'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='refree',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='battle_refree', to='users.player'),
        ),
    ]
