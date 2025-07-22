from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from users.models import PlayerNotification
from .models import PushSubscription
from core.models import Comment, Post
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

class TextPadCommentList(APIView):
    def get(self, request, textpad_id):
        data = get_data.get_textpad_comments(textpad_id)
        return JsonResponse({'comments': data})


class BattleRequestsList(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        data = get_data.battle_requests(request)
        return JsonResponse({'requests': data})


























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
    