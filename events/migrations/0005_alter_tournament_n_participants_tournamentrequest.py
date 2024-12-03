# Generated by Django 4.2.7 on 2024-08-28 00:33

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0085_alter_family_id'),
        ('events', '0004_fightertournament_tournament_fighters'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tournament',
            name='n_participants',
            field=models.IntegerField(),
        ),
        migrations.CreateModel(
            name='TournamentRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=30)),
                ('start_date', models.DateField(default=django.utils.timezone.now)),
                ('n_participants', models.IntegerField()),
                ('rules', models.TextField()),
                ('creator', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.player')),
            ],
        ),
    ]