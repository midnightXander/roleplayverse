# Generated by Django 4.2.7 on 2024-07-11 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0004_alter_battle_id_alter_battlerequest_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battlerequest',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
