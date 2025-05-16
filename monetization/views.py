from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from users.models import Player
from users.users_utility import get_player
import core.views as core_views

def eligible_to_monetization(player:Player):
    return False


@login_required
def index(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    if not eligible_to_monetization(player):
        return redirect('/monetization/requirements')
    # Check if the player is eligible for monetization
    
    n_notifs = core_views.get_notifs(player=player)
    
    return render(request,"monetization/index.html", {
        'player':player,
        'n_notifs': n_notifs,
    })

@login_required
def requirements(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    n_notifs = core_views.get_notifs(player=player)

    #redirect player if eligible
    if eligible_to_monetization(player):
        return redirect('/monetization')
    
    return render(request,"monetization/requirements.html", {
        'player':player,
        'n_notifs': n_notifs,
    })

