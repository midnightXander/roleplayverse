from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.urls import reverse
from django.contrib.auth.models import User,auth
from django.http import JsonResponse,HttpResponseRedirect
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required
from .models import *
from events.models import Tournament
from battles.models import Battle,Challenge
from chat.models import FamilyMessage
import battles.views as battle_views
import users.views as users_views
from pathlib import Path
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import os
import json
from django.views.decorators.csrf import csrf_exempt
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from users.users_utility import get_player
from utility import _time_since,_parse_number,decrypt_message,sendWelcomeEmail,generate_referall_code
import random
from django.contrib.gis.geoip2 import GeoIP2
import re


BASE_DIR = Path(__file__).resolve().parent.parent

def get_characters():
    characters_file = os.path.join(BASE_DIR,"characters/playable_characters.json")
    with open(characters_file,"r") as f:
        characters = json.load(f)
    return characters      


def remove_points(player:Player,points):
    battle_points = player.battle_points
    new_battle_points = battle_points - points
    
    if new_battle_points <=0:
        new_battle_points = 0

    player.battle_points = new_battle_points    
    player.save()

def add_points(player:Player, points:int):
    player.battle_points += points
    player.save()
    



def index(request):
    player = get_player(request.user)
    if player:
        return redirect('/home')
    else:
        return render(request,"core/index.html")

def get_comments(post):
    comments = Comment.objects.filter(post = post)
    return comments

def _get_comment(player:Player,comment:Comment):
    return  {   
            'id': comment.id,
            'author': {
                'player': str(comment.author),
                'username': comment.author.user.username,
                'profile_picture': comment.author.profile_picture.url,
            },
            'comments': len(Comment.objects.filter(post = comment.post)),
            'liked': _liked_comment(player, comment),
            'likes': _parse_number(len(CommentReaction.objects.filter(comment = comment))),
            'body': comment.body,
            'timestamp': _time_since(comment.date_added)  

        } 

def get_comments_dict(player:Player,post:Post):
    comments = Comment.objects.filter(post = post).order_by('-date_added')
    comments_dict = []

    data = [
        {   
            'id': comment.id,
            'author': {
                'id': comment.author.id ,
                'player': str(comment.author),
                'username': comment.author.user.username,
                'profile_picture': comment.author.profile_picture.url,
            },
            'liked': _liked_comment(player, comment),
            'likes': _parse_number(len(CommentReaction.objects.filter(comment = comment))),
            'body': comment.body,
            'timestamp': _time_since(comment.date_added)  

        } for comment in comments
    ]

    for comment in comments:
        comment_dict = model_to_dict(comment)

        if comment_dict['image']:
            comment_dict['image'] = comment.image.url
        else:
            comment_dict['image'] = None

        comments_dict.append(comment_dict)
    

    return data

def get_time_posted(post):
    date_posted = post.date_added
    current_time = datetime.datetime.hour

def get_notifs(player):
    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    notifs = Notification.objects.filter(target = player, read = False)
    challenges = Challenge.objects.filter(target = player)
    n_notifs = len(player_notifs) + len(notifs) + len(challenges)

    if n_notifs == 0:
        return ""
    if n_notifs>9:
        return "9+"
    else:
        return f"{n_notifs}"
        
@login_required
def home(request):


    posts = Post.objects.all()
    battles = Battle.objects.filter(status = "finished")
    

    characters = get_characters()    

    posts = list(posts)
    battles = list(battles)
    #get the feed
    posts_data = [ {
            "type": "post",
            "post": post,
            "comments": get_comments(post),
            "n_comments": len(get_comments(post)),
            "time_posted": _time_since(post.date_added),
        } for post in posts
        ]
    battles_data = [
        {
        "type": "battle",
        "battle": battle
    } for battle in battles
    ]

    feed = posts_data + battles_data
    

    #sort the list of characters
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"]) 

    # player = get_object_or_404(Player, user = request.user )
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    feed,created = Feed.objects.get_or_create(player = player)
    
    feed.posts.clear()
    feed.battles.clear()
    
    feed.save()
    players = Player.objects.exclude( user = request.user)
    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)
    can_invite = False

    fl_message_data = None

    #check if player is in a family 
    if player.family:
        player_family = player.family 
        #check if player is the head of a family to determine if he  can send invites to other players
        if player == player_family.god_father :
            can_invite = True

        family_last_message = FamilyMessage.objects.filter(family = player_family).order_by('-date_sent').first()
        
        if family_last_message:
            content =  decrypt_message(family_last_message.content)[:7]+'...'
            if family_last_message.image:
                content = f'a envoyé une image'
            fl_message_data = {
                "sender":family_last_message.sender.user.username,
                'content': content,
            }
        else:
            fl_message_data = {
                "sender":"sender",
                'content': "Le dernier messaage seras affiché ici",
            }          
    now = datetime.datetime.now()          
    
    challenges = Challenge.objects.filter(target = player).order_by('-date_sent')[:2]
    

    families  = Family.objects.all()
    top_families = sorted(families, key = lambda family : family.points ,reverse=True)[:2]
    events = Tournament.objects.all().order_by('-date_created')[:2]
    to_translate = _("Chats")

    context = {
        
        "posts":posts,
        "players":players,
        'playerName': str(player),
        "player_notifs":player_notifs,
        "player":player,
        "can_invite":can_invite,
        "characters": sorted_characters ,
        "feed":feed,
        "n_notifs":get_notifs(player),
        'fl_message':fl_message_data,
        'top_families': top_families,
        'top_players': users_views._monthly_players_ranking()[:3],
        'battle_cover': random.randint(1,1),
        'events': events,
        "to_translate": to_translate,
        'challenges': challenges
        
        }
    
    
    return render(request,"core/home.html",context)

def _liked_comment(player:Player, comment:Comment):
    liked = False
    reactions = CommentReaction.objects.filter(comment = comment, player = player)
    if reactions.exists():
        liked = True
    return liked 

def _liked_post(player:Player, post:Post):
    liked = False
    reactions = Reaction.objects.filter(post = post, player = player)
    if reactions.exists():
        liked = True
    return liked    

    

def _posts_data(player:Player,posts):
    return [
         {
           "feed_item": "post",
            "id": post.id,
            "author":{  
                        'id':post.author.id,
                        "name":post.author.user.username,
                        'player': str(post.author),
                        'profile_picture':post.author.profile_picture.url
                        },
            'body':post.body,
            'liked': _liked_post(player, post),
            'likes':_parse_number(post.likes),
            'image':post.image.url if post.image else None,
            "comments": get_comments_dict(player,post),
            "n_comments": _parse_number(len(get_comments(post))),
            "time_posted": _time_since(post.date_added),
            'is_favorite': SavedPost.objects.filter(player = player, post = post).exists(),
        } for post in posts
    ]

def _post_data(player:Player, post:Post):
    return {
            "feed_item": "post",
            "id": post.id,
            "author":{  
                        'id':post.author.id,
                        "name":post.author.user.username,
                        'player': str(post.author),
                        'profile_picture':post.author.profile_picture.url
                        },
            'body':post.body,
            'liked': _liked_post(player, post),
            'likes':_parse_number(post.likes),
            'is_favorite': SavedPost.objects.filter(player = player, post = post).exists(),
            'image':post.image.url if post.image else None,
            "comments": get_comments_dict(player,post),
            "n_comments": _parse_number(len(get_comments(post))),
            "time_posted": _time_since(post.date_added),
        }

def get_posts(request):
    player = Player.objects.get(user = request.user)
    feed = Feed.objects.get(player = player)
    #posts criterias:
    #1. family members posts
    #2. Recent posts
    feed_data = []

    #sort both posts and battles
    feed_items = (Post.objects.values('id','date_added').annotate(date=F('date_added')).union(Battle.objects.filter(Q(status = 'finished') |  Q(status = 'ongoing')).values('id','date_ended').annotate(date = F('date_ended')), all=True).order_by('-date'))
    for feed_item in feed_items:
        try:
            post = Post.objects.get(id = feed_item['id'])
            if (post not in feed.posts.all()) and len(feed_data) <=2:
                post_data = _post_data(player,post)
                feed_data.append(post_data)
                feed.posts.add(post)
        except Post.DoesNotExist:
            battle = Battle.objects.get(id = feed_item['id'])    
            if battle not in feed.battles.all() and len(feed_data) <= 2:
                battle_data = battle_views._battle_data(player, battle)
                feed_data.append(battle_data)
                feed.battles.add(battle)

    #feed the object and created the boolean indicating if the object was created or not
    
    # feed.posts.clear()
    posts = []
    battles = []

    #get posts by family members first priority
    # family_posts = Post.objects.filter(
    #     author__family = player.family
    # ).order_by('-date_added')

    
    # for post in family_posts:
    #     if (post not in feed.posts.all()) and (len(battles) + len(posts)) <=2:
            
    #         posts.append(post)
    #         #feed.posts.add(post)
    #         # print(len(feed.posts.all()))
    #         # print("posts_len: ", len(posts))
            
            

    # other_posts = Post.objects.exclude(author__family = player.family).order_by('-date_added')
    # for post in other_posts:
    #     if post not in feed.posts.all() and (len(battles) + len(posts)) <=2 :
    #         posts.append(post)
    #         #feed.posts.add(post)
    #         # print("added other post")

    
    # recent_battles = Battle.objects.filter(Q(status = "finished") |  Q(status = 'ongoing')).order_by('-date_started')
    # for battle in recent_battles:
    #     if battle not in feed.battles.all() and (len(battles) + len(posts)) <=2 :
    #         battles.append(battle)
    #         #feed.battles.add(battle)

    feed.save()
    posts_data = _posts_data(player,posts)
    battles_data = battle_views._battles_data(player,battles)
    
    
    
    # print("FEED",feed_data,len(feed_data))
    #random.shuffle(feed)

    #data = serialize('json',posts)

    #take only 3 feed item at a time    
    return JsonResponse({'data':feed_data[:3]}, safe=False)


def get_notifications(request):
    player = Player.objects.get(user = request.user)
    player_notifs = PlayerNotification.objects.filter(target= player).order_by('-date_sent')
    notifications = Notification.objects.filter(target = player).order_by('-date_sent')

    data = [
        {
            'id':notification.id,
            "content": notification.content,
            'url':notification.url,
            'timestamp': _time_since(notification.date_sent),
            'type':'generic',
        } for notification in notifications
    ]

    return JsonResponse({'status':'success', 'notifications': data})


def _string_found(search_string, main_string):
    pattern = re.compile(re.escape(search_string),re.IGNORECASE)
    return bool(pattern.search(main_string))

def search_all(request, scope = 'global'):
    search_list = []
    if request.method == "POST":
        text = request.POST["text"] 
        searched_users = User.objects.filter(username__icontains = text) 
        searched_families = Family.objects.filter(name__icontains =  text)
        battles = Battle.objects.all().order_by('-date_started')
        searched_battles = []
        searched_players = []
        #if not searched_users:
        for user in searched_users:
            if user.username != "xander_random":
                player = Player.objects.get(user=user)
                searched_players.append({"id":player.id,
                                         "etype":"player",
                                         "username":player.user.username,
                                         "profile_picture":player.profile_picture.url,
                                         })
        player = Player.objects.get(user = request.user)
        for battle in battles:
            
            if _string_found(text, str(battle)):
                battle_data = battle_views._battle_data(player,battle)
                battle_data['etype'] = 'battle'
                searched_battles.append(battle_data)

        families = [{"name":family.name,
                     "etype":"family",
                     "id":family.id,
                     "profile_picture":family.profile_picture.url,
                     } for family in searched_families]
        
        
        search_list = searched_players + families + searched_battles[:3]


        #context = {"searched_players":searched_players}
        #return JsonResponse({"status":"success","searched_players":searched_players})  
        return JsonResponse({"status":"success","search_list":search_list})
    
@login_required
def feed(request):
    player = Player.objects.get(user=request.user)
    posts = Post.objects.all()
    context = {"posts":posts, "player":player}

    return render(request,"feed/index.html",context)

@login_required
def post_page(request, id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    post = get_object_or_404(Post,id= id)
    n_notifs = get_notifs(player)

    comments = Comment.objects.filter(post = post)

    post_data =  {
            "feed_item": "post",
            "id": post.id,
            "author":{  
                        'id':post.author.id,
                        "name":post.author.user.username,
                        'player': str(post.author),
                        'profile_picture':post.author.profile_picture.url
                        },
            'body':post.body,
            'liked': _liked_post(player, post),
            'likes':_parse_number(post.likes),
            'image':post.image.url if post.image else None,
            "comments": get_comments_dict(player,post),
            "n_comments": _parse_number(len(get_comments(post))),
            "time_posted": _time_since(post.date_added),
    }

    if request.method == "POST":
        data = post_data
        return JsonResponse({'status':'success', 'post':data})


    context = {"player":player, "post":post_data, "n_notifs":n_notifs}
    return render(request, "feed/post.html", context)

def create_post(request):
    if request.method == "POST":
        player = Player.objects.get(user = request.user)
        body = request.POST.get("body")
        image = request.FILES.get('image')
        
        if body or image:
            
            new_post = Post.objects.create(author=player,body=body,image = image)
            

        #     new_post_data = {
        #     "feed_item": "post",
        #     "id": new_post.id,
        #     "author":{  
        #                 'id':new_post.author.id,
        #                 "name":new_post.author.user.username,
        #                 'player': str(new_post.author),
        #                 'profile_picture':new_post.author.profile_picture.url
        #                 },
        #     'body':new_post.body,
        #     'liked': _liked_post(player, new_post),
        #     'likes':_parse_number(new_post.likes),
        #     'image':new_post.image.url if new_post.image else None,
        #     "comments": get_comments_dict(player,new_post),
        #     "n_comments": len(get_comments(new_post)),
        #     "time_posted": _time_since(new_post.date_added),
        # }
            new_post_data = _post_data(player,new_post)
            new_post.save()
            return JsonResponse({'status':'success', 'post':new_post_data})

        # return HttpResponseRedirect(reverse('core:home'))    

    return render(request,"feed/new_post.html")

@csrf_exempt
def comment(request,id):    
    player = Player.objects.get(user = request.user)
    comment = get_object_or_404(Comment,id= id)
    if request.method == "DELETE":
        if comment.author ==   player:
            comment.delete()
            return JsonResponse({'status':'success','message':'commentaire Supprimé'})
        return JsonResponse({'status':'error','message':"l'utlisateur n'est pas l'auteur de ce commentaire"})
    
        
        
@csrf_exempt
def post(request,id):    
    player = Player.objects.get(user = request.user)
    post = get_object_or_404(Post,id= id)
    if request.method == "DELETE":
        if post.author ==   player:
            post.delete()
            return JsonResponse({'status':'success','message':'Publication Supprimé'})
        return JsonResponse({'status':'error','message':"l'utlisateur n'est pas l'auteur de cette publication"})
    else:
        comments = Comment.objects.filter(post = post)

        post_data = {
            "author":str(post.author),
            "body":post.body,
            "likes":post.likes,
            "comments":[
                {
                "author":str(comment.author),
                "body":comment.body,
                    } 
                for comment in comments

            ],
                    }
        
        return JsonResponse({"status":"success","post":post_data})
    

@csrf_exempt
def delete_post(request,id):
    if request.method == "POST":
        post  = get_object_or_404(Post, id = id)
        post.delete()
        #return JsonResponse({'status':'success','message':'deleted succesfully'})   
        return HttpResponseRedirect(reverse("core:feed"))
    elif request.method == "DELETE":
        return JsonResponse({'status':'success','message':'Publication Supprimé'})

    
    return JsonResponse({'status':'error','message':'delete failed'})

@login_required
def modify_post(request,id):
    player = get_object_or_404(Player, user=request.user)
    post = get_object_or_404(Post, id = id)

    context = {'post':post, 
               "player":player,
               "n_notifs":get_notifs(player),
               }
    
    if post.author == player:
        if request.method == "POST":
            body = request.POST['body']
            if request.FILES.get('new_image'):
                image = request.FILES['new_image']
                post.image = image
            post.body = body    
            post.save()
            return HttpResponseRedirect(reverse("core:home")) 
    else:
        return HttpResponseRedirect(reverse("core:home"))
               

    return render(request,"feed/modify_post.html",context)

@csrf_exempt
def react_post(request,post_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user) 
        post  = get_object_or_404(Post, id = post_id)
        reactions = Reaction.objects.filter(post = post, player = player)

        reactions_data = [
            {"type":reaction.type,
             "player": str(reaction.player),
             "post": reaction.post.id,
             } for reaction in reactions
        ]
        for reaction in reactions:
            if reaction.player == player:
                print('already liked:',reaction)
                reaction.delete()
                post.likes = post.likes - 1
                
                post.save()
                return JsonResponse({"status":'success','message':'unliked','likes':post.likes})
        # if reactions.exists():
        #     print('already liked:',reactions)
        #     reactions[0].delete()
        #     post.likes = post.likes - 1

        #     reactions[0].save()
        #     post.save()
        #     return JsonResponse({"status":'success','message':'unliked'})
            
        reaction = Reaction.objects.create(
            player = player,
            post = post,
            type = 'like',
        )
        print('new like',reaction)
        post.likes = post.likes + 1
        reaction.save()
        post.save()
        
        
        return JsonResponse({"status":'success',"message":"liked",'likes':post.likes})
    
    return JsonResponse({"status":"error"}) 

@csrf_exempt
def react_comment(request, comment_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user) 
        comment  = get_object_or_404(Comment, id = comment_id)
        reactions = CommentReaction.objects.filter(comment = comment, player = player)

        reactions_data = [
            {
            "type":reaction.type,
            "player": str(reaction.player),
            "comment": reaction.comment.id,
             
            } for reaction in reactions
        ]
        for reaction in reactions:
            if reaction.player == player:
                
                reaction.delete()
                comment.likes = comment.likes - 1
                
                comment.save()
                likes = len(CommentReaction.objects.filter(comment = comment))

                return JsonResponse({"status":'success','message':'unliked','likes': _parse_number(likes)})
        # if reactions.exists():
        #     print('already liked:',reactions)
        #     reactions[0].delete()
        #     post.likes = post.likes - 1

        #     reactions[0].save()
        #     post.save()
        #     return JsonResponse({"status":'success','message':'unliked'})
            
        reaction = CommentReaction.objects.create(
            player = player,
            comment = comment,
            type = 'like',
        )
        
        comment.likes = comment.likes + 1
        if comment.author != player:
            notif = Notification.objects.create(
                target = comment.author,
                content = f'{player} liked your comment: {comment.body[:10]}...',
                url = f'/posts/{comment.post.id}',
            )
            notif.save()

        reaction.save()
        comment.save()
        
        likes = len(CommentReaction.objects.filter(comment = comment))
        return JsonResponse({"status":'success',"message":"liked",'likes':_parse_number(likes)})
    
    return JsonResponse({"status":"error"}) 


def create_comment(request,post_id):
    if request.method == "POST":
        body = request.POST['body']
        if body != "":
            post  = get_object_or_404(Post, id = post_id)
            player = Player.objects.get(user = request.user)
            new_comment = Comment.objects.create(
                author = player,
                post = post,
                body = body,
            )
            

            #send a notification to the post author
            if player != post.author:
                new_notif = Notification.objects.create(
                    target = post.author,
                    content = f'{player} a commenté votre publication',
                    url = f'/posts/{post.id}',
                )
                new_notif.save()
            new_comment.save()
            comment = _get_comment(player, new_comment)
            return JsonResponse({"status":"success","comment":comment
            })
    return JsonResponse({"status":"error","message":"Une erreur est survenu"})


@login_required
def notifications(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    player_notifications = PlayerNotification.objects.filter(
        Q(target = player)
    ).order_by("-date_sent")
    notifications = Notification.objects.filter(target = player).order_by('-date_sent')
    challenges = Challenge.objects.filter(target = player).order_by('-date_sent')
    characters = get_characters()  
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"]) 
    
    #set the notifs to be read once you go to the notifications page
    for notif in player_notifications:
        notif.read = True
        notif.save()

    for notif in notifications:
        notif.read = True
        notif.save()  

    
            

    #n_notifs = len(player_notifications)
    context = {"player":player, 
               "player_notifications": player_notifications,
               'notifications': notifications,
                'challenges': challenges,
                'characters': sorted_characters,
                "n_notifs": get_notifs(player),

               }
    return render(request, "core/notifications.html", context)   




####might be on another app########
@login_required
def battle_points(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')

    if request.method == "POST":
        new_points = request.POST.get("points")
        new_points = int(new_points)
        player.battle_points += new_points
        player.save()
        return HttpResponseRedirect(reverse("core:home"))

    context = {"player":player}
    return render(request,"core/battle_points.html",context)

def favorite(request, id):
    player = Player.objects.get(user = request.user)
    post = get_object_or_404(Post, id = id)

    if request.method == 'POST':
        saved_posts = SavedPost.objects.filter(player = player)
        saved_post_ids = []
        
        #verify if the post is already a saved post from the player and if true,
        #delete it from there instead
        if saved_posts.filter(post = post).exists():
            #delete post from saved posts
            saved_post = SavedPost.objects.get(player = player, post = post)
            saved_post.delete()
            return JsonResponse({"status":'success',
                                 'message':'Publication retirée des favoris'})
        else:
            #add post to saved posts    
            new_saved_post = SavedPost.objects.create(
                player = player,
                post = post,
                date_added = datetime.datetime.now()
            )
            new_saved_post.save()

            return JsonResponse({"status":'success',
                                 'message':'Publication ajoutée aux favoris'})
    #elif request.method == 'DELETE':

    return JsonResponse({"status":'error',
                                 'message':'Une erreur est survenu'})



def tutorials(request):
    return render(request, "core/tutorials.html")

@login_required
def rankings(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')

    context = {
        'player':player,
        'n_notifs':get_notifs(player),
    }
    return render(request, 'core/rankings.html', context )