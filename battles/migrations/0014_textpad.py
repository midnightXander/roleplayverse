# Generated by Django 4.2.7 on 2024-07-12 15:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0051_alter_family_id'),
        ('battles', '0013_alter_battle_refree'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextPad',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('battle', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='battles.battle')),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.player')),
            ],
        ),
    ]