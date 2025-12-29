from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Player,PlayerDefaultImage
from core.models import Notification
from utility import generate_referall_code
from django.contrib.gis.geoip2 import GeoIP2
import random
import core.views as core_views

from .models import ENTRY_POINTS,Player

def init_duel_character(player:Player):
    character = player.duel_character if player.duel_character else {}
    data = {
        "name": str(player),
        'rank': 'Genin',  # Default rank, can be changed later
        'chakra_pool': character.get('chakra_pool', 50),  # Default chakra pool 
        'stamina_pool': character.get('stamina_pool', 100),  # Default stamina pool
        'health': character.get('health', 100),  # Default health
        'xp' : character.get('xp', 0),
        # 'jutsus': request.POST.getlist('skills'),
        'jutsus' : character.get('jutsus',[]),
        "image": player.profile_picture.url
    }
    player.duel_character = data
    player.save()
    return data

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
        init_duel_character(new_player)
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