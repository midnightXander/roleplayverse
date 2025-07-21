from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from api.utility import send_push_notification
import core.views as core_views
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required

from users.users_utility import get_player
from .models import *
from core.models import *
from battles.models import Battle,Challenge, RefreeingProposal
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

  