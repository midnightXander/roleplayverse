from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.urls import reverse
from django.contrib.auth.models import User,auth
from django.http import JsonResponse,HttpResponseRedirect
from monetization.models import Payment
from store.models import Product
from users.models import Player,PlayerNotification,Family
from story.models import StoryCharacter
from story.views import _story_character
from django.contrib.auth.decorators import login_required
from .models import *
from events.models import Tournament
from battles.models import Battle,Challenge, RefreeingProposal
from chat.models import FamilyMessage
import battles.views as battle_views
import users.views as users_views
from pathlib import Path
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import os
import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from users.users_utility import get_country, get_player
from utility import _time_since,_parse_number,decrypt_message,sendWelcomeEmail,generate_referall_code
from api.models import PushSubscription
from api.utility import send_push_notification
import random
from django.contrib.gis.geoip2 import GeoIP2
import re
from . import emails
import praw,time
from api.views import export_battle_data
from store.views import product_data
import requests
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
            'post_id' : comment.post.id,   
            'id': comment.id,
            'author': {
                'player': str(comment.author),
                'username': comment.author.user.username,
                'profile_picture': comment.author.profile_picture.url,
            },
            'parent' : {
                    "id": comment.parent.id,
                    "author": {
                        "id": comment.parent.author.id,
                        "username": comment.parent.author.user.username,
                        "player": str(comment.parent.author),
                        "profile_picture": comment.parent.author.profile_picture.url,
                    },
                } if comment.parent else None,
            'comments': len(Comment.objects.filter(post = comment.post)),
            'liked': _liked_comment(player, comment),
            'likes': _parse_number(len(CommentReaction.objects.filter(comment = comment))),
            'replies' : [ _get_comment(player, reply) for reply in Comment.objects.filter(parent = comment).order_by("-date_added") ],
            'body_full': comment.body,
            'body': comment.body[:197]+'...' if len(comment.body) > 200 else comment.body,
            'timestamp': _time_since(comment.date_added)  

        } 

def get_comments_dict(player:Player,post:Post):
    comments = Comment.objects.filter(post = post).order_by('-date_added')
    comments_dict = []

    data = [
        {   
            'post_id' : comment.post.id,   
            'id': comment.id,
            'author': {
                'id': comment.author.id ,
                'player': str(comment.author),
                'username': comment.author.user.username,
                'profile_picture': comment.author.profile_picture.url,
            },
            'parent' : {
                    "id": comment.parent.id,
                    "author": {
                        "id": comment.parent.author.id,
                        "username": comment.parent.author.user.username,
                        "player": str(comment.parent.author),
                        "profile_picture": comment.parent.author.profile_picture.url,
                    },
                } if comment.parent else None,
            'liked': _liked_comment(player, comment),
            'likes': _parse_number(len(CommentReaction.objects.filter(comment = comment))),
            'body_full': comment.body,
            'body': comment.body[:197]+'...' if len(comment.body) > 200 else comment.body,
            'replies' : [ _get_comment(player, reply) for reply in Comment.objects.filter(parent = comment).order_by("-date_added") ],
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
def onboarding(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    

    context = {
        "player":player,
        "n_notifs":get_notifs(player),
    }
    
    return render(request,"core/onboarding.html",context)


@login_required
def home(request):

    # emails.send_emails(["ralldidierselemani@gmail.com","franckbodo81@gmail.com"], "Le Shinobi Mayhem t'attends!!","Le Shinobi Mayhem t'attends!!",
    #                    "Le tirage au sort du tournoi Shinobi Mayhem a été effectué, les regles ont ete fixé, ton adversaire t'attends pour entamer les hostilités !!" )

    posts = Post.objects.all()
    battles = Battle.objects.filter(status = "finished")
   
    g = GeoIP2()
    # ip = "134.201.250.155"
    # try:
    #     country = g.country(ip)
    # except Exception as e:
    #     print(f"Country error: {e}")
    #     country = 'unknown'    
    # print("Country: ", country)

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
    
    story_characters = StoryCharacter.objects.filter(player = player)
    if not story_characters.exists():
        return redirect('story:index')
    
    player.country = get_country(request)
    print(player.country)
    print(f"{player} IP: ",request.META.get('REMOTE_ADDR'))
    player.ip_adress = request.META.get('REMOTE_ADDR')
    player.save()

    #export_battle_data()  

    feed,created = Feed.objects.get_or_create(player = player)
    
    feed.announcements.clear()
    feed.posts.clear()
    feed.battles.clear()
    feed.daily_content.clear()
    feed.story_characters.clear()
    
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
    events = Tournament.objects.filter(status__in = ['registering', 'ongoing', 'not_started']).order_by('-date_created')[:2]
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
        'top_players': users_views._monthly_players_ranking()[:2],
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
            'body_full': post.body,
            'body': post.body[:200]+'...' if post.body and len(post.body) > 200 else (post.body if post.body else '' ),
            'liked': _liked_post(player, post),
            'likes':_parse_number(post.likes, True),
            'image':post.image.url if post.image else None,
            "comments": get_comments_dict(player,post),
            "n_comments": _parse_number(len(get_comments(post)), True),
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
                        'profile_picture':post.author.profile_picture.url,
                        'nickname': post.author.nickname if post.author.nickname else post.author.user.username,
                        },
            
            'body_full': post.body,
            'body': post.body[:200]+'...' if post.body and len(post.body) > 200 else (post.body if post.body else '' ),
            'liked': _liked_post(player, post),
            'likes':_parse_number(post.likes,True),
            'is_favorite': SavedPost.objects.filter(player = player, post = post).exists(),
            'image':post.image.url if post.image else None,
            "comments": get_comments_dict(player,post),
            "n_comments": _parse_number(len(get_comments(post)),True),
            "time_posted": _time_since(post.date_added),
        }

def _daily_content_data(player:Player, content:ContentPost):
    
    return {
            "feed_item": content.type,
            "id": content.id,
            'title':content.title,
            'body_full': content.body,
            'body': content.body[:200]+'...' if content.body and len(content.body) > 200 else (content.body if content.body else '' ),
            # 'liked': _liked_content(player, content),
            # 'likes':_parse_number(content.likes,True),
            # 'is_favorite': Savedcontent.objects.filter(player = player, content = content).exists(),
            'image':content.image_url if content.image_url else None,
            # "comments": get_comments_dict(player,content),
            # "n_comments": _parse_number(len(get_comments(content)),True),
            "time_posted": _time_since(content.date_added),
            'reactions' : content.reactors.all().count(),
            'comments' : ContentComment.objects.filter(content = content).count(),
            'most_reaction' : content.most_made_reaction()['type'] if content.most_made_reaction() else '👍'

    }

def _annoucement_data(announcement:Announcement):
    return {
            "feed_item": "announcement",
            "id": announcement.id,
            # "author":{  
            #             'id':announcement.author.id,
            #             "name":announcement.author.user.username,
            #             'player': str(announcement.author),
            #             'profile_picture':announcement.author.profile_picture.url,
            #             'nickname': announcement.author.nickname if announcement.author.nickname else announcement.author.user.username,
            #             },
            'title' : announcement.title,
            'body_full': announcement.content,
            'body': announcement.content[:200]+'...' if announcement.content and len(announcement.content) > 200 else (announcement.content if announcement.content else '' ),
            # 'liked': _liked_announcement(player, announcement),
            # 'likes':_parse_number(announcement.likes,True),
            'image':announcement.image.url if announcement.image else None,
            # "comments": get_comments_dict(player,announcement),
            # "n_comments": _parse_number(len(get_comments(announcement)),True),
            "time_posted": _time_since(announcement.date_added),
            'redirect': announcement.redirect_url,
            'url' : announcement.url
        }

def get_posts(request):
    
    player = Player.objects.get(user = request.user)
    feed = Feed.objects.get(player = player)
    #posts criterias:
    #1. family members posts
    #2. Recent posts
    feed_data = []


    #sort both posts and battles
    feed_items = (Post.objects.values('custom_id','date_added')
                  .annotate(date=F('date_added'))
                  .union(Battle.objects.filter(status__in = ['finished', 'ongoing', 'waiting_refree'])
                         
                    .values('custom_id','date_ended')
                    .annotate(date = F('date_ended')), all=True)
                    .union(ContentPost.objects.values('custom_id', 'date_added')
                    .annotate(date = F('date_added')),all=True)
                    .union(StoryCharacter.objects.values('custom_id', 'created_at')
                    .annotate(date = F('created_at')),all=True)

                    .order_by('-date'))
    

    

    #put ongoing battles first before all others
    feed_limit = 10

    # Put the latest annoucement first
    announcement = Announcement.objects.filter(active = True).order_by('-date_added').first()
    if announcement:
        announcement_data = _annoucement_data(announcement)
        feed_data.append(announcement_data)
        feed.announcements.add(announcement)  

    # for feed_item in feed_items:
    #     try: 
    #         battle = Battle.objects.get(custom_id = feed_item['custom_id'])    
    #         if battle not in feed.battles.all() and len(feed_data) <= feed_limit-2 and battle.status == 'ongoing':
    #             battle_data = battle_views._battle_data(player, battle)    
    #             feed_data.append(battle_data)
    #             feed.battles.add(battle)     

    #     except Battle.DoesNotExist:
    #         pass        
    #take the two latest Memes and add to feed
    for content in ContentPost.objects.all().order_by('-date_added')[:2]:
        if content not in feed.daily_content.all():
            content_data = _daily_content_data(player,content)
            feed_data.append(content_data)
            feed.daily_content.add(content)

    random.shuffle(feed_data)

    for feed_item in feed_items:
        try:
            post = Post.objects.get(custom_id = feed_item['custom_id'])
            
            if (post not in feed.posts.all()) and len(feed_data) <=feed_limit:
                post_data = _post_data(player,post)
                feed_data.append(post_data)
                feed.posts.add(post)
        except Post.DoesNotExist:
            try:
                battle = Battle.objects.get(custom_id = feed_item['custom_id'])    
                if battle not in feed.battles.all() and len(feed_data) <= feed_limit:
                    battle_data = battle_views._battle_data(player, battle)
                    if battle.status == 'waiting_refree' and RefreeingProposal.objects.filter(player = player, battle = battle).exists():
                        pass
                    elif battle.status == 'waiting_refree' and len(RefreeingProposal.objects.filter(battle = battle)) > feed_limit:
                        pass
                    else:    

                        feed_data.append(battle_data)
                        feed.battles.add(battle)
            
            except Battle.DoesNotExist:
                try:
                    content = ContentPost.objects.get(custom_id = feed_item['custom_id'])
                    if content not in feed.daily_content.all() and len(feed_data) <= feed_limit:
                        content_data = _daily_content_data(player,content)
                        feed_data.append(content_data)
                        feed.daily_content.add(content)
                
                except ContentPost.DoesNotExist:
                    # for character in StoryCharacter.objects.all():
                    #     character.custom_id = generate_custom_id()
                    #     character.save()
                    story_character = StoryCharacter.objects.filter(custom_id = feed_item['custom_id']).first()
                    if story_character not in feed.story_characters.all() and len(feed_data) <= feed_limit:
                        story_character_data = _story_character(story_character)
                        last_textpad = story_character_data['last_textpad']
                        story_character_data['body_full'] = last_textpad
                        story_character_data['body'] = last_textpad[:200]+'...' if last_textpad and len(last_textpad) > 200 else (last_textpad if last_textpad else '' ),
                        
                        feed_data.append(story_character_data)
                        feed.story_characters.add(story_character)

                    
    random.shuffle(feed_data)

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
    # posts_data = _posts_data(player,posts)
    # battles_data = battle_views._battles_data(player,battles)
    product = random.choice(Product.objects.all())
    _product_data = product_data(product)
    
    # print("FEED",feed_data,len(feed_data))
    #feed_data = feed_data[:feed_limit]
    #feed_data = random.shuffle(feed_data)

    #data = serialize('json',posts)

    #take only 3 feed item at a time    
    return JsonResponse({'data':feed_data[:feed_limit], 'product':_product_data}, safe=False)


def fetch_players(request):
    player  = get_player(request.user)
    if not player:
        return JsonResponse({'status': 'error'}, status = 401)
    to = request.GET.get('to','challenge')
    if to == 'challenge':
        active_players = Player.objects.exclude(id = player.id).order_by('-last_seen')[:10]
        active_players = [ users_views._player_data(player) for player in active_players ]
        top_players = users_views._monthly_players_ranking()[:4]

        to_challenge = active_players + top_players
        random.shuffle(to_challenge)

    return JsonResponse({'status': 'error', 'players': to_challenge})

def get_notifications(request):
    player = Player.objects.get(user = request.user)
    player_notifs = PlayerNotification.objects.filter(target= player).order_by('-date_sent')
    notifications = Notification.objects.filter(target = player).order_by('-date_sent')
    challenges = Challenge.objects.filter(target = player, answered = False).order_by('-date_sent')
    characters = get_characters()  
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"]) 
    
    for notification in notifications:
        notification.read = True
        notification.save()
    for notification in player_notifs:
        notification.read = True
        notification.save()    

    data = [
        {   
            'type': 'generic',
            'id':notification.id,
            "content": notification.content,
            'url':notification.url,
            'timestamp': _time_since(notification.date_sent),
            'type':'generic',
            'image' : notification.img_url,
            'clicked' : notification.clicked,
            'read' : notification.read,
        } for notification in notifications
    ]
    challenges = [
        {
            'type': 'challenge',
            'id': challenge.id,
            'sender': {
                'id': challenge.sender.id,
                'username': challenge.sender.user.username,
                'player': str(challenge.sender),
                'profile_picture': challenge.sender.profile_picture.url,
            },
            'sender_character': challenge.sender_character,
            'timestamp': _time_since(challenge.date_sent),
        } for challenge in challenges
    ]
    invites = [
        {
            'id' : invite.id,
            'family' : {
                'id' : invite.family.id,
                'name' : invite.family.name,
                'profile_picture' : invite.family.profile_picture.url,
                'god_father' : {
                    'username' : invite.family.god_father.username,
                }
            }

        } for invite in player_notifs.filter(notif_type = 'invite').order_by('-date_sent')
    ]

    requests = [
        {
            'id' : request.id,
            'sender' : {
                'id' : request.sender.id,
                'username' : request.sender.user.username,
                'player' : str(request.sender),
                'rank' : request.sender.rank,
                'progression' : request.sender.progression,
            }
            
        } for request in player_notifs.filter(notif_type = 'request').order_by('-date_sent')
    ]

    return JsonResponse({'status':'success', 'notifications': data, 'invites': invites, 'requests' : requests, 'challenges' : challenges, 'characters':sorted_characters})


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
            if user.username != "xander_randomo":
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
            postid = len(Post.objects.all()) + 1
            new_post = Post.objects.create(
                #id = postid,
                author=player,body=body,image = image)
            
            new_post_data = _post_data(player,new_post)
            new_post.save()
            if body and len(body) > 30:
                users = User.objects.exclude(username = player.user.username)
                users = users.order_by('?')[:50] #get 15 random users
                subscriptions_id =[ sub.id for sub in PushSubscription.objects.all() ] 
                from .tasks import send_bulk_notification
                payload = {
                            'title': f'{player}',
                            'body': f'{new_post.body[:30]}...',
                            'icon': f'{player.profile_picture.url}',
                            'url': f'/posts/{new_post.id}'
                        },
                print(subscriptions_id)
                #send_bulk_notification.delay(subscriptions_id, payload)

                # for subscription in subscriptions:
                #     send_push_notification(
                #         subscription,
                #         {
                #             'title': f'{player}',
                #             'body': f'{new_post.body[:30]}...',
                #             'icon': f'{player.profile_picture.url}',
                #             'url': f'/posts/{new_post.id}'
                #         },
                #     )
                for user in users:
                    send_push_notification(
                        PushSubscription.objects.filter(user = user).last(),
                        payload
                    )

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

def get_post_comments(request, post_id):
    player  = get_player(request.user)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(parent=None, post = post).order_by("-date_added")
    data = [_get_comment(player, comment) for comment in comments]
    
    return JsonResponse({ 'status': 'success', 'comments' : data}, safe=False)     
        
        
@csrf_exempt
def post(request,id):    
    player = Player.objects.get(user = request.user)
    post = get_object_or_404(Post,id= id)
    if request.method == "DELETE":
        if post.author ==   player:
            post.delete()
            return JsonResponse({'status':'success','message':'Publication Supprimé'})
        return JsonResponse({'status':'error','message':"l'utlisateur n'est pas l'auteur de cette publication"})
    elif request.method == 'GET':
        post_data = _post_data(player, post)
        return JsonResponse({"status":"success","post":post_data})
    
    else:
        return JsonResponse({'status':'error', 'message':'Bad request'})

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
        # try:
        #     emails.send_email(
        #         subject = "Test email",
        #         title = "Test email",
        #         body = """
        #         <h2>This is a test email</h2>
        #         <p>Test email body</p>
        #         <p>Test email body</p>
        #         <a href = "roleplayverse.live" class = "button">Click here</a>
        #         """,
        #         recipient_email = player.user.email,
        #     )
        #     print("email sent")
        # except Exception as e:
        #     print("Error sending email:", e)    

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

        #Send Push Notification if likes exceeds 10
        if post.likes == 5:
            send_push_notification(PushSubscription.objects.filter(user = post.author.user).last(), {
                'title': 'Votre publication a été aimé par 5 personnes',
                'body': f'Votre publication a été aimé par 5 personnes',
                'icon': '/static/images/logo/logo_1.png'
            },  )
        
        
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
        #Send Push Notification if likes exceeds 10
        if likes == 10:
            send_push_notification(PushSubscription.objects.filter(user = comment.author.user).last(), {
                'title': 'Votre commentaire a été aimé par 10 personnes',
                'body': f'Votre commentaire sur la publication de {comment.post.author} a été aimé par 10 personnes',
                'icon': '/static/images/logo/logo_1.png'
            })
        return JsonResponse({"status":'success',"message":"liked",'likes':_parse_number(likes)})
    
    return JsonResponse({"status":"error"}) 


def create_comment(request,post_id):
    if request.method == "POST":
        body = request.POST['body']
        if body != "":
            post  = get_object_or_404(Post, id = post_id)
            player = Player.objects.get(user = request.user)
            parent_id = request.POST.get("parent_id")
            parent = None
            notification_text = f"{player} a commenté votre publication" 
            if parent_id:
                parent = get_object_or_404(Comment, id=parent_id)
                notification_text = f"{player} a repondu ton commentaire sur une publication" 
            new_comment = Comment.objects.create(
                author = player,
                post = post,
                body = body,
                parent = parent,
            )

            #send a notification to the post author
            if player != post.author:
                new_notif = Notification.objects.create(
                    target = post.author,
                    content = notification_text,
                    url = f'/posts/{post.id}',
                    img_url = f"{player.profile_picture.url}"
                )
                new_notif.save()
                #send a push notification to the post author
                send_push_notification(PushSubscription.objects.filter(user = post.author.user).last(), {
                    'title': notification_text,
                    'body': f'{new_comment.body[:20]}...',
                    'icon': f"{player.profile_picture.url}"
                })
            if new_comment.parent and new_comment.parent.author != new_comment.author:
                new_notif = Notification.objects.create(
                    target = new_comment.parent.author,
                    content = f"{player} a repondu a ton commentaire sur une publication",
                    url = f'/posts/{post.id}',
                    img_url = f"{new_comment.author.profile_picture.url}"
                )
                new_notif.save()
                #send a push notification to the post author
                send_push_notification(PushSubscription.objects.filter(user = new_comment.parent.author.user).last(), {
                    'title': f"{new_comment.author} a repondu a ton commentaire sur une publication",
                    'body': f'{new_comment.body[:20]}...',
                    'icon': f"{new_comment.author.profile_picture.url}",
                    'url' : f'/posts/{post.id}',
                },
                user = new_comment.parent.author.user
                )  


            new_comment.save()
            comment = _get_comment(player, new_comment)
            return JsonResponse({"status":"success","comment":comment
            })
    return JsonResponse({"status":"error","message":"Une erreur est survenu"})

def _content_reactions_data(content_reactor:ContentReactor):
    return {
        'date_added' : _time_since(content_reactor.date_added),
        'reaction' : content_reactor.type,
        'player' : content_reactor.player.user.username,
        }

def react_to_content(request, content_id):
    content = get_object_or_404(ContentPost, id = content_id)
    player = get_player(request.user)

    if request.method == 'POST':
        
        reaction = request.POST.get('reaction','😂')
        
        reactors = content.reactors.all()

        if player in reactors:
            player_reaction = ContentReactor.objects.get(player = player, content = content)
            if reaction == player_reaction.type:
                content.reactors.remove(player)
            else:
                player_reaction.type = reaction  
                player_reaction.save()      
        else:
            content.reactors.add(player, through_defaults={'type': reaction})
            

        content.save()
        reactions = [ _content_reactions_data(reactor) for reactor in ContentReactor.objects.filter(content = content)]

        return JsonResponse({'status':'success', 'reactions': reactions})

def _content_comment_data(comment:ContentComment):
    data:dict = {    
                "content_id" : comment.content.id,
                "id": comment.id,
                "text": comment.text,
                'body_full': comment.text,
                'body': comment.text[:197]+'...' if len(comment.text) > 200 else comment.text,
                "author": {
                    'id' : comment.author.id,
                    "player": str(comment.author),
                    "username": comment.author.user.username,
                    'profile_picture' : comment.author.profile_picture.url,
                },
                'parent' : {
                    "id": comment.parent.id,
                    "author": {
                        "id": comment.parent.author.id,
                        "username": comment.parent.author.user.username,
                        "player": str(comment.parent.author),
                        "profile_picture": comment.parent.author.profile_picture.url,
                    },
                    # "body_full" : comment.text,
                    # "body": comment.parent.text[:50] + '...' if len(comment.parent.text) > 50 else comment.parent.text,
                } if comment.parent else None,
                "timestamp":  _time_since(comment.date_added),
                'likes' : 0,
                'replies' : [ _content_comment_data(reply) for reply in ContentComment.objects.filter(parent = comment).order_by("-date_added") ],
                #'is_reply' : contentComment.objects.filter(parent = ).exists()
            },
    
    
    return data 

def add_content_comment(request, content_id):
    if request.method == 'POST':
        content = get_object_or_404(ContentPost, id=content_id)
        author = get_player(request.user)  # Assuming Player is linked to User
        text = request.POST.get("body")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(ContentComment, id=parent_id)

        comment = ContentComment.objects.create(
            content=content, author=author, text=text, parent=parent
        )
        comment.save()

        
        if comment.parent:
            if comment.parent.author != comment.author:
                new_notif = Notification.objects.create(
                    target = comment.parent.author,
                    url = f'/contents/{content.id}',
                    content = f"{comment.author} a repondu a ton commentaire sur un meme",
                    img_url = comment.author.profile_picture.url
                )
                new_notif.save()
                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = comment.parent.author.user).last(),
                    {
                    'title' : f"Nouvelle reaction sur ton meme",
                    'body' : f"{comment.author} a repondu a ton commentaire sur un meme",
                    'url' : f'/contents/{content.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                    
                )
            
                

                
                
        return JsonResponse({
            "status": "success",
            "comment": _content_comment_data(comment)
        })

def get_content_comments(request, content_id):
    content = get_object_or_404(ContentPost, id=content_id)
    comments = ContentComment.objects.filter(parent=None, content = content).order_by("-date_added")
    data = [_content_comment_data(comment) for comment in comments]
    
    return JsonResponse({ 'status': 'success', 'comments' : data}, safe=False) 

@login_required
def content_post_page(request, id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    content = get_object_or_404(ContentPost,id= id)
    product_ad  = random.choice(Product.objects.all()) 
    n_notifs = get_notifs(player)

    content_data =  _daily_content_data(player, content)
    _product = product_data(product_ad) if product_ad else None

    if request.method == "POST":
        data = content_data
        return JsonResponse({'status':'success', 'content':data, 'product':_product})


    context = {"player":player, "content":content_data, "n_notifs":n_notifs}
    return render(request, "feed/content.html", context)

@login_required
def notifications(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    player_notifications = PlayerNotification.objects.filter(
        Q(target = player)
    ).order_by("-date_sent")
    notifications = Notification.objects.filter(target = player).order_by('-date_sent')
    challenges = Challenge.objects.filter(target = player, answered = False).order_by('-date_sent')
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

@csrf_exempt
def mark_notif_as_read(request, notification_id):
    notification = get_object_or_404(Notification,id = notification_id)
    notification.clicked = True
    notification.save()

    return JsonResponse({'status':'success'})

@csrf_exempt
def mark_all_notifs_as_read(request):
    player = get_player(request.user)
    notifications = Notification.objects.filter(target = player).order_by('-date_sent')
    
    for notification in notifications:
        notification.read = True
        notification.clicked = True
        notification.save()

    return JsonResponse({'status':'success'})




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
        # return HttpResponseRedirect(reverse("core:home"))
        return JsonResponse({"status":"success", "message":"Battle points updated successfully", "points": player.battle_points})

    context = {"player":player}
    return render(request,"core/battle_points.html",context)

def battle_points_success(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')


    new_points = request.GET.get("points")
    order_id = request.GET.get('order_id')
    new_points = int(new_points)
    
    try:
        payment = Payment.objects.get(order_id = order_id)
        print("already paid")
    except Payment.DoesNotExist: 
        player.battle_points += new_points
        player.save()
        payment = Payment.objects.create(
            player = player,
            amount = new_points,
            order_id = order_id,
            # type = 'battle_points',
            status = 'completed',
        )
        payment.save()
        print("Now paid")
        #send a notification to the player
        new_notif = Notification.objects.create(
            target = player,
            content = f'Vous avez reçu {new_points} jetons de combat',
            url = '/battle_points',
            img_url = player.profile_picture.url
        )
        new_notif.save()
        send_push_notification(
            PushSubscription.objects.filter(user = player.user).last(),
            {
                'title': 'jetons de combat reçus',
                'body': f'Vous avez reçu {new_points} jetons de combats',
                'icon': player.profile_picture.url,
                'url': '/notifications'
            }
        )
    context = {"player":player, 'n_notifs': get_notifs(player)}
    return render(request,"core/battle_points_sucess.html", context)


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

def ezoic_file(request):
    return render(request, 'core/ezoic-3jZENPJ2HyQHll4Ye2ZCBVIua866XL.html', {})