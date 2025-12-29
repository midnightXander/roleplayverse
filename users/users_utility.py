from .models import Player,referall_points,Family
from core.models import Notification, models
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2
from core import emails
from api.utility import send_push_notification
from api.models import PushSubscription

def get_player(user:User):
    try:
        player = Player.objects.get(user = user)
        
        #player.profile_picture.url = "https://i.pinimg.com/736x/60/1b/04/601b0478fe7f09eda50d8e478f847e58.jpg"
        player.init_duel_character()
        player.save()
        return player
    except:
        return None
def get_country(request):
    g = GeoIP2()
    ip = request.META.get('REMOTE_ADDR')
    try:
        country = g.country(ip)
    except Exception as e:
        print(f"Country error: {e}")
        country = 'unknown'    

    return country       

def refer_player(referall_code, new_player:Player = None):
    try:
        player = Player.objects.get(referall_code = referall_code)
        player.battle_points += referall_points
        player.rp_credits += 10
        new_player.godfather = player
        new_player.save()
        player.save()
        send_push_notification(
            PushSubscription.objects.filter(player = player.user).first(),
            {
                'title': 'Recompense',
                'body': f'Tu as gagné {referall_points} de jetons et des credits RP en parrainant un ami!',
                'icon': '/static/images/logo/logo_1.png',
            },
            player.user
        )
        Notification.objects.create(target = player,
                                    content = f'Tu as gagné {referall_points} de jetons et des credits RP en parrainant un ami!',
                                    url = f'/users/{new_player.user.username}'
                                    )

        #send email to player congratulating him for the referall points
        # emails.send_email(
        #     recipient_email = player.user.email,
        #     title = "Félicitations!",
        #     subject = "Vous avez gagné des points de parrainage!",
        #     body = f"""
        #     <h2>Bonjour {player},</h2>
        #     <p>vous avez gagné {referall_points} points de parrainage en parrainant un ami!</p>
        #     <p><strong>{{ notification_message }}</strong></p>
        #     """,
        #     language = player.user.language
        # )
        
        #Update creator link data if player is a creator
        # creator = Creator.objects.filter(player = player).first() 
        # if creator:
        #     url = f"https://roleplayverse.live/?rc={referall_code}"
        #     link,created = CreatorLink.objects.get_or_create(link = url, creator = creator)
        #     data = {
        #         'clicks' : int(link.data.get("clicks",0)) + 1,
        #         'signups' : int(link.data.get("signups",0)) + 1,
        #         'active_users' : link.data.get("active_users",0)
        #     }
        #     link.data = data
        #     link.save()

        

    except Exception as e:
        print(f"Referall error: {e}")
        return False

def add_player_to_family(family:Family, player:Player): 
    """Adds a player to a family"""
    if player.family != None:
        return False
    else:
        family.members.add(player)
        player.family = family
        player.save()
        return True 

def remove_player_from_family(family:Family, player:Player): 
    """Removes a player from a family"""
    if player.family == None:
        return False
    else:
        family.members.remove(player)
        player.family = None
        player.save()
        return True      