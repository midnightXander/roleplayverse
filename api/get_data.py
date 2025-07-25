from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from api.utility import send_push_notification
import core.views as core_views
from store.models import Product
from store.views import product_data
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required

from users.users_utility import get_player
from users.views import _player_data
from utility import _parse_number, _time_since, get_characters
from .models import *
from core.models import *
from battles.models import Battle, BattleRequest,Challenge, RefereeRating, RefreeingProposal, Rule, TextPad, TextPadComment,battle_status
import battles.views as battle_views




def feed_items(request):
    
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
                    .annotate(date = F('date_added')),
                    all=True)      
                    .order_by('-date'))
    

    

    #put ongoing battles first before all others
    feed_limit = 10

    # Put the latest annoucement first
    announcement = Announcement.objects.filter(active = True).order_by('-date_added').first()
    if announcement:
        announcement_data = core_views._annoucement_data(announcement)
        feed_data.append(announcement_data)
        feed.announcements.add(announcement)  

    for feed_item in feed_items:
        try: 
            battle = Battle.objects.get(custom_id = feed_item['custom_id'])    
            if battle not in feed.battles.all() and len(feed_data) <= feed_limit-2 and battle.status == 'ongoing':
                battle_data = battle_views._battle_data(player, battle)    
                feed_data.append(battle_data)
                feed.battles.add(battle)     

        except Battle.DoesNotExist:
            pass        
    #take the two latest Memes and add to feed
    for content in ContentPost.objects.all().order_by('-date_added')[:2]:
        if content not in feed.daily_content.all():
            content_data = core_views._daily_content_data(player,content)
            feed_data.append(content_data)
            feed.daily_content.add(content)

    for feed_item in feed_items:
        try:
            post = Post.objects.get(custom_id = feed_item['custom_id'])
            
            if (post not in feed.posts.all()) and len(feed_data) <=feed_limit:
                post_data = core_views._post_data(player,post)
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
                
                content = ContentPost.objects.get(custom_id = feed_item['custom_id'])
                if content not in feed.daily_content.all() and len(feed_data) <= feed_limit:
                    content_data = core_views._daily_content_data(player,content)
                    feed_data.append(content_data)
                    feed.daily_content.add(content)
                    


    #feed the object and created the boolean indicating if the object was created or not
    
    # feed.posts.clear()
    posts = []
    battles = []

    feed.save()

    #take only 3 feed item at a time    
    return feed_data[:feed_limit]

def get_post_comments(request, post_id):
    player  = get_player(request.user)
    post = get_object_or_404(Post, id=post_id)
    comments = Comment.objects.filter(parent=None, post = post).order_by("-date_added")
    data = [core_views._get_comment(player, comment) for comment in comments]
    
    return { 'comments' : data}     

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

    return {'notifications': data, 'invites': invites, 'requests' : requests, 'challenges' : challenges, 'characters':sorted_characters}


def get_textpads(request, battle_id):
    battle = Battle.objects.get(id = battle_id)
    textpads = TextPad.objects.filter(battle = battle)
    player = get_player(request.user)

    textpads_data = [
        {
            'id' : textpad.id,
            "owner": textpad.owner.user.username,
            "text": textpad.text,
            "valid": textpad.valid,
            "character": battle_views.get_textpad_character(battle,textpad),
            "time_since": core_views._time_since(textpad.date_sent),
            'index': index + 1,
            'comment' : textpad.refree_comment,
            'date_validated': core_views._time_since(textpad.date_validated) if textpad.date_validated else 'pas encore validé',
            'comment' : textpad.refree_comment,
            'hidden_action' : textpad.hidden_action if player == battle.refree or battle.status == 'finished' else None,
            'reactions' : textpad.reactors.all().count(),
            'comments' : TextPadComment.objects.filter(textpad = textpad).count(),
            'most_reaction' : textpad.most_made_reaction()['type'] if textpad.most_made_reaction() else '👍'

        } for index,textpad in enumerate(textpads)
    ] 

    return textpads_data

def get_textpad_comments(textpad_id):
    textpad = get_object_or_404(TextPad, id=textpad_id)
    comments = TextPadComment.objects.filter(parent=None, textpad = textpad).order_by("-date_added")
    data = [battle_views._textpad_comment_data(comment) for comment in comments]
    
    return data 

def battle_requests(request):
    player = get_player(request.user)
    requests = BattleRequest.objects.filter(hidden = False).exclude(sender = player).order_by('-date_sent')
    requests_data = battle_views._battle_requests_data(player, requests)

    return requests_data


def filter_battle(request, filter_num):
        #filter_num = int(request.GET['filter'])
        player = get_player(request.user)
        battles = Battle.objects.filter(status = battle_status[filter_num]).order_by('-date_started')
        if filter_num == 0:
            battles = battles.exclude(
                Q(initiator=player) | Q(opponent=player)
            )
        message = "..."
        battles_data = battle_views._battles_data(player, battles)
        return {"message":message ,"battles":battles_data}


@login_required
def _battle_room(request,battle_id, player:Player):
    
    battle = Battle.objects.get(id=battle_id)
    
    battle_views.update_battle_spectators(player,battle)
    battle.viewers += 1
    battle.save()
    
    rules = Rule.objects.filter(battle = battle)
    rules_data = [{
        'text': rule.text
    } for rule in rules ]

    role = "Spectateur"
    
    if player == battle.refree:
        role = "Arbitre"
        
    elif player == battle.initiator or player == battle.opponent:
        role = "Combattant"    

    ch_jutsus = ''
    character = ''
    i_character =  battle_views._character(battle.i_character)
    o_character = battle_views._character(battle.o_character)
    if player == battle.initiator:
        ch_jutsus = battle_views._character_jutsus(battle.i_character)
        character = battle_views._character(battle.i_character)
    if player == battle.opponent:
        ch_jutsus = battle_views._character_jutsus(battle.o_character)    
        character = battle_views._character(battle.o_character)


    textpads = TextPad.objects.filter(battle = battle)

    if len(textpads)>0:
        last_textpad = textpads.last()
        l_sender  = last_textpad.owner
    else:
        l_sender = None    

    textpads_data = [
        {
            "textpad":battle_views._textpad_data(player,textpad),
            "character":battle_views.get_textpad_character(battle, textpad)
        }
        for textpad in textpads 
    ]
    
    #get the last player to send a  textpad
    def can_rate(battle:Battle):
        if player == battle.refree:
            return False
        elif battle.type == 'friendly':
            return False
        elif RefereeRating.objects.filter(battle = battle, player = player).exists():
            return False
        elif player != battle.initiator and player != battle.opponent:
            return False    
        elif len(RefereeRating.objects.filter(battle = battle)) >= 2:
            return False
        elif battle.status != 'finished':
            return False
        else:
            return True

            
    product = random.choice(Product.objects.all())
    _product_data = product_data(product)
    
    context = {

               "battle":battle_views._battle_data(player,battle),
               "isFighter" : player in [battle.initiator, battle.opponent],
               "rules":rules_data, 
               "rules_set": len(rules) >= 3,
               "textpads":textpads_data,
            #    "last_textpad": textpads_data[-1] if len(textpads_data)>0 else "",
               'jutsus': ch_jutsus,
               'i_character': i_character,
               'o_character': o_character,
               'spectators':  _parse_number(len(battle.spectators.all()) + battle.viewers,True),
                "last_sender":_player_data(l_sender),
                "role":role,
                "can_rate": can_rate(battle),
                'referee_rated': battle_views.referee_rated(battle),
                'product': _product_data
                 }
    


    if battle_views.referee_rated(battle):
        initiator_rating = RefereeRating.objects.get(player = battle.initiator,battle = battle)
        def _rating_data(rating:RefereeRating):
            return {
                'player': {
                    'username': str(rating.player),
                    'player': rating.player.user.username,
                },
                'fairness': rating.fairness,
                'communication': rating.communication,
                'timeliness':rating.timeliness,
                'comment' : rating.comment
            }
        opponent_rating = RefereeRating.objects.get(player = battle.opponent,battle = battle)
        ratings = [
            { 'category': 'Timeliness', 'initiator': initiator_rating.timeliness, 'opponent': opponent_rating.timeliness  },
            {'category': 'Communication', 'initiator': initiator_rating.communication, 'opponent': opponent_rating.communication},
            {'category': 'Fairness', 'initiator': initiator_rating.fairness, 'opponent': opponent_rating.fairness }
        ]
        opponent_rating = RefereeRating.objects.filter(player = battle.opponent).last()
        context['initiator_rating'] = _rating_data(initiator_rating)
        context['opponent_rating'] = _rating_data(opponent_rating)
        context['ratings'] = ratings

    return context
    