from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player,PlayerDefaultImage
from core.models import Notification
from utility import generate_referall_code
from django.contrib.gis.geoip2 import GeoIP2
import random
import core.views as core_views

from .models import ENTRY_POINTS
@receiver(post_save, sender = User)
def create_player(sender, instance, created, **kwargs):
    if created:

        #Think of the Possible name conflicts
        new_player = Player.objects.create(
            user = instance,
            country = 'unknown',
            gender = 'male',
            referall_code = generate_referall_code(instance.username),
        ) 
        profile_pics = PlayerDefaultImage.objects.all()
        random_pic = random.choice(profile_pics)
        new_player.profile_picture = random_pic.image

        #Get the country of the user using the ip address
        g = GeoIP2()
        try:
            ip = instance.last_login_ip
            country = g.country(ip)['country_name']
            new_player.country = country
        except:
            pass
        
        core_views.add_points(new_player, ENTRY_POINTS)
        new_player.save()
        new_notif = Notification.objects.create(
                    target = new_player,
                    url = '/battles',
                    content = f'Bienvenue sur RolePlay Verse {new_player} pourquoi pas commencé un combat amicale pour voir comment ça se passe ici?'
                )
        new_notif.save()