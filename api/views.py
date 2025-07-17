from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PushSubscription
from core.models import Post
from pywebpush import webpush, WebPushException
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from battles.models import *
from dotenv import load_dotenv
import os
import core.views as core_views 
from . import get_data


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


class feed(APIView):
    def get(self, request):
        user = request.user
        player = Player.objects.filter(user=user).first()
        if not player:
            return JsonResponse({'status': 'error', 'message': 'Player not found'}, status=404)
        
        posts = Post.objects.all()
        posts_data = [core_views._post_data(player, post) for post in posts ]
        feed_items = get_data.feed_items(request)
        
        return JsonResponse({ 'status':'success', 'username':f'{user}', 'posts': posts_data, 'feed_items': feed_items }, safe=False)

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
    