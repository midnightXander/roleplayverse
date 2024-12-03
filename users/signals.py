from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player
from core.models import Notification
from utility import generate_referall_code
from django.contrib.gis.geoip2 import GeoIP2

@receiver(post_save, sender = User)
def create_player(sender, instance, created, **kwargs):
    if created:

        #Think of the Possible name conflicts
        new_player = Player.objects.create(
            user = instance,
            country = 'Cameroon',
            gender = 'male',
            referall_code = generate_referall_code(instance.username),
        ) 
        new_player.save()
        new_notif = Notification.objects.create(
                    target = new_player,
                    url = '#',
                    content = f'Welcome to Roleplay verse {new_player} Why not start a friendly battle to see how it works?'
                )
        new_notif.save()