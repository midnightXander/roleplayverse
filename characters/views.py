from django.http import JsonResponse
from django.shortcuts import render
from .models import Character
from users.models import Player
from utility import get_characters, get_solo_battle_characters
from django.contrib.auth.decorators import login_required

def create_characters(name,jutsu,image):
    new_character = Character.objects.create(
        name = name,
        image = image
    )
    new_character.set_justu_field(jutsu)
    new_character.save()

@login_required
def index(request):
    player = Player.objects.get(user=request.user)
    characters = get_solo_battle_characters()
    sorted_characters = sorted(characters, key = lambda item: item["name"])
    context = {"characters":sorted_characters, "player":player}
    return render(request,'characters/index.html',context)

def all_characters(request):
    characters = get_characters()
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"])
    return JsonResponse({ 'characters': sorted_characters })

    