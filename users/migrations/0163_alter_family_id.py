# Generated by Django 4.2.7 on 2024-12-05 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0162_auto_20241205_1116'),
    ]

    operations = [
       
        migrations.RemoveField(
            model_name='family',
            name='id',
        ),
        migrations.AddField(
            model_name='family',
            name='id',
            field=models.BigAutoField(primary_key=True),
        ),
        migrations.AlterField(
            model_name='related_model',
            name='family',
            field=models.ForeignKey(on_delete=models.CASCADE, to='users.family'),
        )

    ]
