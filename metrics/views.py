from django.shortcuts import render
from django.shortcuts import render,get_object_or_404,redirect
from django.db.models import Q,QuerySet
from django.db.models import Case, When,F
from django.urls import reverse
from django.contrib.auth.models import User,auth
from django.http import JsonResponse,HttpResponseRedirect
from store.models import AffiliateProduct
from users.models import Player,PlayerNotification,Family
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
import datetime
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.utils.translation import gettext as _
from users.users_utility import get_player
from utility import _time_since,_parse_number,decrypt_message,sendWelcomeEmail,generate_referall_code
from api.models import PushSubscription
from api.utility import send_push_notification
import random
from django.contrib.gis.geoip2 import GeoIP2
import re


def ad_click(request):


    # camapign = request.GET.get('')
    # url = request.path

    if request.method == 'POST':
        url = request.POST.get('url', '')
        image = request.POST.get('image', '')

        data = {
            'url' : f'{url}',
            'image' : f'{image}'
        }

        product = AffiliateProduct.objects.filter(link = url).first()
        if product:
            product.clicks += 1
            product.save()

        try:
            new_adclick = AdClick.objects.create(
                user = request.user,
                data = data
            )
            new_adclick.save()
            return JsonResponse({'status': 'success'})
        except Exception as ex:
            print(f'An error occured: {e}')
            return JsonResponse({'status': 'error'})
    else:
        return JsonResponse({'status': 'error'})


