# Generated by Django 4.2.7 on 2024-09-08 08:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battles', '0030_alter_refreetest_expriry_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refreetest',
            name='situation1',
            field=models.ImageField(blank=True, choices=[('battles/situations/1.jpg', 'battles/situations/1.jpg'), ('battles/situations/2.jpg', 'battles/situations/2.jpg'), ('battles/situations/3.jpg', 'battles/situations/3.jpg')], upload_to=''),
        ),
        migrations.AlterField(
            model_name='refreetest',
            name='situation2',
            field=models.ImageField(blank=True, choices=[('battles/situations/4.jpg', 'battles/situations/4.jpg'), ('battles/situations/5.jpg', 'battles/situations/5.jpg'), ('battles/situations/6.jpg', 'battles/situations/6.jpg')], upload_to=''),
        ),
    ]