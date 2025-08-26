from datetime import datetime
from django.shortcuts import render,get_object_or_404,redirect
from api.models import PushSubscription
from api.utility import send_push_notification
from battles.models import Battle
from blog.models import BlogPost
from django.http import HttpResponseRedirect,Http404, JsonResponse
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth import logout,login,authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from events import models as events_models
from users.models import Player
from .moderator_utility import get_moderator
from .models import *
from battles.models import *
import events.views as events_views
import  core.models as core_models
import os
from django.db.models import Q,QuerySet
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from battles.views import add_refree, player_progress, update_points, update_rank
from events.views import _update_round,init_tournament
load_dotenv()
import json

def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        l_code = request.POST.get('signinCode')
        password = request.POST.get('password')

        if not email or not l_code or not password:
            messages.error(request,"Entrez tout les champs")
            return HttpResponseRedirect(reverse("moderator:signin"))
        
        try:
            user = User.objects.get(email=email)
            moderator = Moderator.objects.get(user = user )
        except:
            messages.error(request,"L'utisateur n'est pas moderateur")
            return HttpResponseRedirect(reverse("moderator:signin")) 
        

        

        if l_code != moderator.login_code:
            messages.error(request,"Le code de  connexion est incorrect")
            return HttpResponseRedirect(reverse("moderator:signin")) 
        
        elif password != os.environ.get('M_PASSWORD'):
            messages.error(request,"Le mot de passe de  moderateur est incorrect")
            return HttpResponseRedirect(reverse("moderator:signin")) 


        #user_auth = auth.authenticate(username = user.username, password = user.password)
        #auth.login(request,user)
        return HttpResponseRedirect(reverse("moderator:index"))
        # if user_auth is not None:
        #     auth.login(request,user_auth)
        #     return HttpResponseRedirect(reverse("moderator:index"))
        # else:
        #     messages.error(request,"Informations incorrect")
        #     return HttpResponseRedirect(reverse("moderator:signin"))
        
    return render(request, "moderator/signin.html")    

# @login_required('/moderator/signinxyz')
def index(request):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    player_emails = [ user.email for user in User.objects.all() ]
    players = Player.objects.all()
    
    return render(request, "moderator/index.html",{
        'moderator': moderator,
        'player_emails': player_emails,
        'countries' : player_countries(players),
        'active_players' : active_players(players)
    })
    
        
# @login_required('/moderator/signinxyz')
def create_post(request):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    
    if request.method == 'POST':
        title = request.POST['title']
        keywords = request.POST.get('keywords', '')
        meta_description = request.POST.get('description', '')
        content = request.POST['content']
        image = request.FILES['cover']
        leading = request.POST['leading']
        category = request.POST['category']
        
        new_post = BlogPost.objects.create(
            category = category,
            title = title,
            text = content,
            image = image,
            leading = leading,
            keywords = keywords,
            owner = moderator.user,
            meta_description = meta_description
        )
        new_post.save()
        return HttpResponseRedirect(reverse('moderator:index'))
    
    return render(request, "moderator/blog/create_post.html")

# @login_required('/moderator/signinxyz')
def edit_blog_post(request,post_id):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    post = get_object_or_404(BlogPost, id = post_id)
    
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES['cover']
        leading = request.POST['leading']
        category = request.POST['category']
        
        post.title = title
        post.text = content
        post.image = image
        post.leading = leading
        post.category = category
        
        post.save()
        return HttpResponseRedirect(reverse('moderator:index'))
    
    return render(request, "moderator/blog/edit_post.html",{
        'post':post
    })

@csrf_exempt
def notify_all_players(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        url = request.POST.get('url', '/')
        if not title or not body:
            return JsonResponse({'status': 'error', 'message': 'Veuillez remplir tous les champs.'})
        message = {
            'title': title,
            'body': body,
            'url': url,
            'icon': '/static/images/logo/logo_1.png'
        }

        players = User.objects.all()
        for player in players:
            send_push_notification(
                subscription = PushSubscription.objects.filter(user=player).last(),
                message = message,
                user = player
            )
        messages.success(request, "Notification envoyée à tous les joueurs.")
        return JsonResponse({'status': 'success', 'message': 'Notification envoyée à tous les joueurs.'})
    
@csrf_exempt
def notify_player(request, identifier):
    if request.method == 'POST':
        title = request.POST.get('title')
        body = request.POST.get('body')
        url = request.POST.get('url', '/')
        if not title or not body:
            return JsonResponse({'status': 'error', 'message': 'Veuillez remplir tous les champs.'})
        message = {
            'title': title,
            'body': body,
            'url': url,
            'icon': '/static/images/logo/logo_1.png'
        }

    
        user = User.ojects.filter(email = identifier).first() or User.objects.filter(username = identifier).first()
        if not user:
            return JsonResponse({'status': 'error', 'message': 'Utilisateur non trouvé.'})
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Joueur non trouvé.'}) 
        send_push_notification(
            subscription = PushSubscription.objects.filter(user=user).last(),
            message = message,
            user = user
        )
        messages.success(request, f"Notification envoyée à {user}.")
        return JsonResponse({'status': 'success', 'message': 'Notification envoyée à tous les joueurs.'})    

@csrf_exempt
def add_player_as_refree(request, email):
    try:
        user = User.objects.get(email=email)
        player = Player.objects.get(user=user)
        add_refree(player)
        return JsonResponse({'status': 'success', 'message': f"{player} ajouté en tant que refree."})
    except Exception as e:
        print(f"Erreur lors de l'ajout du joueur  en tant que arbitre: {e}")
        return JsonResponse({'status': 'error', 'message': 'Erreur lors de l\'ajout du joueur en tant que arbitre.'})

@csrf_exempt    
def update_tournament_round(request, battle_id):
    try:
        battle = Battle.objects.get(id=battle_id)
        _update_round(battle)
        return JsonResponse({'status': 'success', 'message': 'Round mis à jour avec succès.'})
            
    except Exception as e:
        print(f"Erreur lors de la mise à jour du round du tournoi: {e}")
        return JsonResponse({'status': 'error', 'message': 'Erreur lors de la mise à jour du round du tournoi.'})

@csrf_exempt    
def start_tournament(request, tournament_id):
    try:
        tournament = events_models.Tournament.objects.get(id=tournament_id)
        init_tournament(tournament)
        return JsonResponse({'status': 'success', 'message': 'Tournament initiated.'})
            
    except Exception as e:
        print(f"Erreur lors de l'initialisation du tournoi: {e}")
        return JsonResponse({'status': 'error', 'message': f"Erreur lors de l'initialisation du tournoi: {e}"})    
    
@csrf_exempt
def end_battle(request, battle_id):
    battle = Battle.objects.get(id = battle_id)

    winner_name = request.GET.get('winner', '')
    winner = battle.initiator if str(winner_name).lower().strip() == str(battle.i_character).lower().strip() else battle.opponent

    message = "Ce combat est deja terminé"
    if not battle.winner and request.method == 'POST':
        loser = battle.initiator if winner == battle.opponent else battle.opponent
        message = "La latence n'est pas depassé" 
            
        #END BATTLE
        battle.winner = winner 
        battle.status = battle_status[3]
        battle.date_ended = datetime.now()
        battle.defeat_motif = "latency"

        progress =  player_progress(battle=battle,loser_rank = loser.rank)
        winner.progression +=  progress
        
        #update the player's rank if progression reached 100%
        update_rank(winner)
        update_points(family = winner.family, battle=battle, member_progress=progress)
        winner.award_credits(20)

        winner.save()
        battle.save()
            
        if(battle.type == 'tournament'):
            events_views._update_round(battle)
        battle.can_send_textpad = False
        
        battle.save()    
        win_notif = core_models.Notification.objects.create(
                    target = winner,
                    url = f'/battles/battle_room/{battle.id}',
                    content = f"Tu as été declaré  vainqueur de ton combat contre {loser} par latence"
                    )
        send_push_notification(
            PushSubscription.objects.filter(user=winner.user).last(),
            {
                "title": "Tu as remporte ton combat",
                "body": f"Tu as été declaré  vainqueur de ton combat contre {loser} par latence",
                "url": f"https://roleplayverse.live",
                'icon' : '/static/images/logo/logo_1.png',
            },
            winner.user,
            ) 
        win_notif.save()

        lose_notif = core_models.Notification.objects.create(
                    target = loser,
                    url = f'/battles/battle_room/{battle.id}',
                    content = f"Tu as perdu ton combat contre {winner} par latence"
                )
        lose_notif.save()  
        send_push_notification(
            PushSubscription.objects.filter(user=loser.user).last(),
            {
                "title": "Tu as perdu ton combat",
                "body": f"Tu as perdu ton combat contre {winner} par latence",
                "url": f"/notifications",
                'icon' : '/static/images/logo/logo_1.png',
            },
            loser.user,
        )
        
            
        return JsonResponse({'status':'success','message': 'combat terminé'})
    return JsonResponse({'status':'error','message': message})


def player_countries(players: QuerySet[Player]):
    countries = {}
    for player in players:
        country = player.country
        country_data = countries.get(country)
        if country_data:
            count = country_data.get('count', 1) 
            countries[country]['count'] = count + 1
        else:
            countries[country] = {
                'name' : country,
                'count' : 1,
            }
    countries_list = []
    for country,data in countries.items():
        countries_list.append(data)
        

    return countries_list    

def active_players(players:QuerySet[Player]):
    active_count = 0
    for player in players:
        last_seen = player.last_seen
        now  = timezone.now()
        difference = now - last_seen
        if difference.days <= 3:
            active_count += 1

    active_players = {
        'count': active_count,
        'percentage' : int(active_count/players.count() * 100)
    }        

    return active_players       

