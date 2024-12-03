from .models import Player,referall_points
from core.models import models
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.gis.geoip2 import GeoIP2

def get_player(user:User):
    try:
        player = Player.objects.get(user = user)
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

def refer_player(referall_code):
    try:
        player = Player.objects.get(referall_code = referall_code)
        player.battle_points += referall_points
        #send email to player congratulating him for the referall points
        
        player.save()

    except:
        return    