# Generated by Django 4.2.7 on 2024-12-05 09:34

from django.db import migrations
from django.db import models
import  uuid 
class Migration(migrations.Migration):

    dependencies = [
        ('users', '0159_familybadge_alter_family_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name= 'Family',
            name='id',
            field=models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False),
        ),
    ]
