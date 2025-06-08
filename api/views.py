from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import PushSubscription
from pywebpush import webpush, WebPushException
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User

from dotenv import load_dotenv
import os


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
        return JsonResponse({ 'status':'success', 'username':f'{user}' }, safe=False)

    