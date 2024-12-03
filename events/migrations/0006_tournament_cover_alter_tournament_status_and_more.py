# Generated by Django 4.2.7 on 2024-08-29 07:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0086_alter_family_id'),
        ('events', '0005_alter_tournament_n_participants_tournamentrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='cover',
            field=models.ImageField(default='default_cover.jpg', upload_to=''),
        ),
        migrations.AlterField(
            model_name='tournament',
            name='status',
            field=models.CharField(choices=[('waiting_refrees', 'waiting_refrees'), ('not_started', 'not_started'), ('ongoing', 'ongoing'), ('finished', 'finished')], default='waiting_refrees', max_length=20),
        ),
        migrations.CreateModel(
            name='TournamentRefreeRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('player', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.player')),
                ('tournament', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='events.tournament')),
            ],
        ),
    ]