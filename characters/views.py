from django.shortcuts import render
from .models import Character
from users.models import Player
from utility import get_characters


def create_characters(name,jutsu,image):
    new_character = Character.objects.create(
        name = name,
        image = image
    )
    new_character.set_justu_field(jutsu)
    new_character.save()

def index(request):
    player = Player.objects.get(user=request.user)
    characters = get_characters()
    sorted_characters = sorted(characters["playable_characters"], key = lambda item: item["name"])
    context = {"characters":sorted_characters, "player":player}
    return render(request,'characters/index.html',context)
