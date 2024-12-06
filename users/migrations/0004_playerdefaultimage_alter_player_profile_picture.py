# Generated by Django 4.2.7 on 2024-12-06 15:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_player_profile_picture'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerDefaultImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='players/profile_pics/')),
            ],
        ),
        migrations.AlterField(
            model_name='player',
            name='profile_picture',
            field=models.ImageField(default='static/images/profile_pictures/4.jpg', upload_to='players/profile_pics/'),
        ),
    ]
