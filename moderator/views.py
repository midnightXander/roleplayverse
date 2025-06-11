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
import os
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from battles.views import add_refree
from events.views import _update_round
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
    return render(request, "moderator/index.html",{
        'moderator': moderator,
        'player_emails': player_emails
    })
    
        
# @login_required('/moderator/signinxyz')
def create_post(request):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    
    if request.method == 'POST':
        title = request.POST['title']
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
            owner = moderator.user
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
def notify_player(request, email):
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

    
        user = get_object_or_404(User, email=email)
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