# Generated by Django 4.2.7 on 2024-09-20 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0126_alter_family_id'),
        ('battles', '0035_alter_battle_refreeing_rating'),
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_character', models.CharField(blank=True, max_length=40)),
                ('target_character', models.CharField(blank=True, max_length=40)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.player')),
                ('target', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='target', to='users.player')),
            ],
        ),
    ]
