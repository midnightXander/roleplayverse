# Generated by Django 4.2.7 on 2024-06-18 22:34

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Family',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=25)),
                ('bio', models.CharField(max_length=40)),
                ('points', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
                ('position', models.IntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('challenge_head', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='challenge_heads', to=settings.AUTH_USER_MODEL)),
                ('god_father', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Families',
            },
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rank', models.CharField(choices=[('E', 'E'), ('D', 'D'), ('C', 'C'), ('B', 'B'), ('B+', 'B+'), ('A', 'A'), ('A+', 'A+'), ('S', 'S'), ('SS', 'SS'), ('SSS', 'SSS')], default='E', max_length=3)),
                ('nickname', models.CharField(blank=True, max_length=30)),
                ('pseudo', models.CharField(blank=True, max_length=30)),
                ('country', models.CharField(choices=[('Cameroon', 'Cameroon'), ('Congo', 'Congo')], max_length=80)),
                ('p_character', models.CharField(choices=[('Naruto', 'Naruto'), ('Sasuke', 'Sasuke')], max_length=30)),
                ('authorized_to_fight', models.BooleanField(blank=True, default=False)),
                ('family', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='users.family')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]