from .models import Moderator
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse

def get_moderator(user:User):
    try:
        moderator = Moderator.objects.get(user = user)
        return moderator
    except:
        return None