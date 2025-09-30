from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from battles.views import _battle_data
from users.models import Badge, PlayerNotification
from users.users_utility import get_player
from users.views import _player_data
from .models import PushSubscription
from core.models import Comment, Notification, Post
from pywebpush import webpush, WebPushException
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from battles.models import *
from dotenv import load_dotenv
import os
import core.views as core_views 
import users.views as user_views 
from . import get_data
from . import post_data as post_functions


@csrf_exempt
def save_subscription(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        subscription, created = PushSubscription.objects.update_or_create(
            user = request.user,
            endpoint = data.get('endpoint'),
            defaults = {
                'auth_key' : data.get('keys', {}).get('auth'),
                'p256dh_key' : data.get('keys', {}).get('p256dh')
            }
        )
        
        return JsonResponse({'status': 'subscription saved'})
    return JsonResponse({'status': 'error, unauthorized or bad request'}, status=400)

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

class Feed(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        
        posts = Post.objects.all()
        posts_data = [core_views._post_data(player, post) for post in posts ]
        feed_items = get_data.feed_items(request)
        
        return JsonResponse({ 'status':'success', 'username':f'{user}', 'posts': posts_data, 'feed_items': feed_items }, safe=False)

class PostApi(APIView):
    def get(self, request, pk):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        post = Post.objects.filter(id = pk).first()
        data = core_views._post_data(player, post) if post else None
        if not post:
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
        return JsonResponse({ 'status':'success', 'post':data }, safe=False)

    def delete(self, request, pk):
        user = request.user
        player = Player.objects.filter(user=user).first()
        post = Post.objects.filter(id = pk).first()
        if not post:
            return JsonResponse({'status': 'error', 'message': 'Post not found'}, status=404)
        if post.author != player:
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this post'}, status=403)
        post.delete()
        return JsonResponse({'status': 'success', 'message': 'Post deleted successfully'}, status=200)           

class PostListCreate(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        posts = Post.objects.all()
        posts_data = [core_views._post_data(player, post) for post in posts ]
    
        return JsonResponse({ 'status':'success', 'posts':posts_data }, safe=False)
    
    
    def post(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            post = post_functions.create_post(request)
            return JsonResponse({'post': post}, status=200)

class FavoritePostsList(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        data = get_data.favorite_posts(request)
    
        return JsonResponse({ 'status':'success', 'posts' : data }, safe=False)

class PostReactionListCreate(APIView):
    # def get(self, request, post_id):
    #     user = request.user
    #     player = Player.objects.filter(user=user).first()
    #     if not player:
    #         return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        # posts = Post.objects.all()
        # posts_data = [core_views._post_data(player, post) for post in posts ]
    
        # return JsonResponse({ 'status':'success', 'posts':posts_data }, safe=False)
    
    
    def post(self, request, post_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            data = post_functions.react_post(request, post_id)
            return JsonResponse({'data': data}, status=200)

class CommentApi(APIView):
    def get(self, request, id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        comment = Comment.objects.filter(id = id).first()
        if not comment:
            return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)
        data = core_views._get_comment(player, comment)
        return JsonResponse({'status': 'success', 'comment': data}, status=200)
    

    def delete(self, request, id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        comment = Comment.objects.filter(id = id).first()
        if not comment:
            return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)
        if comment.author != player:
            return JsonResponse({'status': 'error', 'message': 'You are not authorized to delete this comment'}, status=403)
        comment.delete()
        return JsonResponse({'status': 'success', 'message': 'Comment deleted successfully'}, status=200)

class CommentListCreate(APIView):
    def get(self, request, post_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        comments = Comment.objects.filter(parent=None, post__id=post_id).order_by("-date_added")
        data = [core_views._get_comment(player, comment) for comment in comments]
        return JsonResponse({'status': 'success', 'comments': data}, status=200)
    
    def post(self, request, post_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            comment = post_functions.create_comment(request, post_id)
            return JsonResponse({'comment': comment}, status=200)

class CommentReactionListCreate(APIView):
    # def get(self, request, post_id):
    #     user = request.user
    #     player = Player.objects.filter(user=user).first()
    #     if not player:
    #         return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        # posts = Post.objects.all()
        # posts_data = [core_views._post_data(player, post) for post in posts ]
    
        # return JsonResponse({ 'status':'success', 'posts':posts_data }, safe=False)
    
    
    def post(self, request, comment_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            data = post_functions.react_comment(request, comment_id)
            return JsonResponse({'data': data}, status=200)

class NotificationLst(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        data = get_data.get_notifications(request)
        
        return JsonResponse({'status': 'success', 'notifications': data}, status=200)
    
class TextPadListCreate(APIView):
    def get(self, request, battle_id):
        data = get_data.get_textpads(request,battle_id)
        return JsonResponse({'data': data})
    
    def post(self, request, battle_id):
        data = post_functions.send_textpad(request, battle_id)
        return JsonResponse({'textpad': data}, status=200)

class TextpadReactionListCreate(APIView):
    # def get(self, request, post_id):
    #     user = request.user
    #     player = Player.objects.filter(user=user).first()
    #     if not player:
    #         return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)

        # posts = Post.objects.all()
        # posts_data = [core_views._post_data(player, post) for post in posts ]
    
        # return JsonResponse({ 'status':'success', 'posts':posts_data }, safe=False)
    
    
    def post(self, request, textpad_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'message': 'Player not found'}, status=404)
        else:
            data = post_functions.react_to_textpad(request, textpad_id)
            return JsonResponse({'data': data}, status=200)

class TextPadCommentList(APIView):
    def get(self, request, textpad_id):
        data = get_data.get_textpad_comments(textpad_id)
        return JsonResponse({'comments': data})
    
    def post(self, request, battle_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            comment = post_functions.send_textpad(request, battle_id)
            return JsonResponse({'comment': comment}, status=200)

class BattleRequestsListCreate(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        data = get_data.battle_requests(request)
        return JsonResponse({'requests': data})
    
    def post(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            battle_request = post_functions.request_battle(request)
            return JsonResponse({'battle_request': battle_request}, status=200)

class BattleAccept(APIView):
    def post(self, request, request_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        else:
            data = post_functions.accept_battle(request, request_id)
            return JsonResponse({'data': data}, status=200)    

class BattleRoom(APIView):
    def get(self, request, battle_id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        battle_data = get_data._battle_room(request, battle_id, player)

        return JsonResponse({'battle_data': battle_data})


class ChallengeList(APIView):
    def get(self, request, name):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        data = get_data.challenges(request, name)
        return JsonResponse(data)
    

class Challenge(APIView):
    def get(self, request, id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        
        data = _battle_data(player, Battle.objects.filter(id = id).first())
        return JsonResponse(data) 


    def post(self, request, id):
        user = request.user
        player = Player.objects.filter(user=user).first()
        action = request.GET.get('action')
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        
        if action == "send":
            data = post_functions.send_challenge(request, id)
        elif action == "answer":
            data = post_functions.answer_challenge(request, id)
        else: data = {}    
        return JsonResponse(data)

class CurrentPlayer(APIView):
    def get(self, request):
        user = request.user
        player = get_player(user)
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        player_data = _player_data(player)

        return JsonResponse({'player': player_data}, status = 200)    

class TopPlayersFamilies(APIView):
    def get(self, request):
        entity = request.GET.get('e')
        players = user_views._monthly_players_ranking()
        families  = Family.objects.all()
        top_families = sorted(families, key = lambda family : family.points ,reverse=True)
        top_families_data = user_views._families_data(top_families)
        if entity == 'players':
            return JsonResponse({'players': players}, status = 200) 
        if entity == 'families':
            return JsonResponse({'families':top_families_data}, status = 200)     
        return JsonResponse({'players': players, 'families':top_families_data}, status = 200)   

class Families(APIView):
    def get(self, request):
        families  = Family.objects.all()
        families_data = user_views._families_data(families)
        return JsonResponse({'families':families_data}, status = 200)
    
    def post(self, request):
        user = request.user
        player = get_player(user)
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        name = request.data["familyName"]
        description = request.data.get("family-bio")
        profile_pic = request.data.get("family-picture")
        #all_families = list(Family.objects.all())
        if player.family:
            return JsonResponse({'message': 'Tu es deja dans une famille, quitte ta famille actuel pour en créer une'}, status=400)

        elif Family.objects.filter(name=name).exists():
            return JsonResponse({'message': 'Une famille avec ce nom existe deja'}, status=400)
        elif not profile_pic:
            return JsonResponse({'message': 'Tu dois ajouter une photo de profile'}, status=400)
        else:
            new_position = len(Family.objects.all()) + 1
            new_family = Family.objects.create(
                name=name,
                god_father = request.user,
                position = new_position,
                description = description,
                )
            if profile_pic:
                new_family.profile_picture = profile_pic
                
            #user = User.objects.get(username=request.user.username)
            player = Player.objects.get(user=request.user)
            player.family = new_family   

            #ADD The GodFather badge to the player
            godfather_badge = Badge.objects.get(title = "GodFather")
            player.badges.add(godfather_badge)

            new_family.save()
            player.save()
            
            new_notif = Notification.objects.create(
                target = player,
                content = "Felicitation, tu es desormais un parrain de famille! et si tu commencais a recruter quelques membres ?",
                url = f"/users/family/{new_family.id}",
            )

            new_notif.save()
            family_data = user_views._family_data(new_family)
            return JsonResponse({'message': 'Famille crée avec succés', 'family':family_data}, status=200)
        #return JsonResponse({'message': 'Request error'}, status=400)


class Chats(APIView):
    def get(self, request):
        chats_data = get_data.chats(request)
        print(chats_data)
        return JsonResponse(chats_data, status = 200)

class PrivateChat(APIView):
    def get(self, request, receiver_name):
        chat_data = get_data.private_chat(request, receiver_name)
        
        return JsonResponse(chat_data, status = 200)

class FamilyChat(APIView):
    def get(self, request, family_name):
        chat_data = get_data.family_chat(request, family_name)
        return JsonResponse(chat_data, status = 200)

class FamilyMessages(APIView):
    def get(self, request, family_name):
        messages_data = get_data.get_family_messages(request, family_name)
        return JsonResponse(messages_data, status = 200)
    
class FamilyMessage(APIView):    
    def delete(self, request, message_id):
        response = post_functions.delete_family_message(request, message_id)
        return JsonResponse(response, status = 200)  

class PrivateMessages(APIView):
    # wss://' + https://roleplayverse.live + /ws/chat/private/'+ room +  "/
    def get(self, request, receiver_id):
        messages_data = get_data.get_private_messages(request, receiver_id)
        return JsonResponse(messages_data, status = 200)

class PrivateMessage(APIView):
    def delete(self, request, message_id):
        response = post_functions.delete_private_message(request, message_id)
        return JsonResponse(response, status = 200)    

class Search(APIView):
    def get(self, request, query):
        search_data = get_data.search(request, query)
        return JsonResponse(search_data, status = 200)



def export_battle_data():
    # This function is a placeholder for exporting battle data.
    # You can implement the logic to export battle data as needed.

    battles = Battle.objects.all()

    for battle in battles:
        textpads = TextPad.objects.filter(battle=battle).order_by('date_sent')
        if len(textpads) >= 2:
            for textpad_1,textpad_2 in zip(textpads[::2], textpads[1::2]):
                if textpad_1 and textpad_2:
                    try:
                        data = {
                            'text_1' : { 'character' :battle.i_character, 'text': textpad_1.text},
                            'text_2' : { 'character' :battle.o_character, 'text': textpad_2.text},
                        }
                        print(data)
                    except Exception as e:
                        print(f"Error exporting data for battle {battle.id}: {e}")    
        else:
            continue

    #return JsonResponse({'status': 'success', 'message': 'Battle data exported successfully.'})
    return {'status': 'success', 'message': 'Battle data exported successfully.'}
    