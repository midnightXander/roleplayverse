from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.contrib.auth.models import User
from api.utility import send_push_notification
import core.views as core_views
from users.models import Player,PlayerNotification,Family
from django.contrib.auth.decorators import login_required
from .models import *
from core.models import *
from battles.models import Battle,Challenge, RefreeingProposal
import battles.views as battle_views


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
            
            new_post_data = core_views._post_data(player,new_post)
            new_post.save()
            if body and len(body) > 30:
                users = User.objects.exclude(username = player.user.username)
                users = users.order_by('?')[:50] #get 15 random users
                for user in users:
                    send_push_notification(
                        PushSubscription.objects.filter(user = user).last(),
                        {
                            'title': f'{player}',
                            'body': f'{new_post.body[:30]}...',
                            'icon': f'{player.profile_picture.url}',
                            'url': f'/posts/{new_post.id}'
                        },
                    )

            return {'post':new_post_data} 