from django.shortcuts import get_object_or_404, redirect, render
from core.views import get_notifs
from users.models import Player
from users.users_utility import get_player
from ai.views import generate_json_content
from ai.prompts import story_characater_scenario_prompt, story_character_background_prompt, story_continue_prompt, story_evaluate_and_continue, story_start_prompt
from .models import *
import json, random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os
import json
from django.views.decorators.csrf import csrf_exempt

def getAffinityIcon(affinity):
    affinities = {
        'Fire' : '🔥',
        'Water' : '💧',
        'Lightning' : '⚡',
        'Earth' : '🪨',
        'Wind' : '🌪',
    }
    icon = affinities.get(affinity, '🌀')
    return icon

def _story_character(character:StoryCharacter):
    ch = character.character
    data = character.character_data
    #data['rank'] = ch.get('rank', 'Genin')
    data['id'] = character.id
    data['story'] = ch.get('story')
    data['affinity_icon'] = getAffinityIcon(data.get('affinity'))
    challenge = StoryChallenge.objects.filter(character = character).first()
    last_textpad = StoryTextPad.objects.filter(challenge = challenge).last()

    if last_textpad:
        data['last_textpad'] = last_textpad.text
    else:
        data['last_textpad'] = ch.get('story')    

    return data


@login_required
def index(request):
    player = get_player(request.user)
    return render(request, "story/index.html", {
        "player" : player,
        "n_notifs": get_notifs(player),
    })

@login_required
def create_character(request):
    player = get_player(request.user)

    if request.method == "POST":
        name = request.POST.get('name')
        gender = request.POST.get('gender')
        affinity = request.POST.get('affinity')
        origin = request.POST.get('origin')
        traits = json.loads(request.POST.get('traits'))
        jutsus = json.loads(request.POST.get('jutsus'))
        description = request.POST.get('description')
        avatar = request.POST.get('avatar')

        

        if player.battle_points >= 1:
            prompt_data = {
                'name' : name,
                'gender' : gender,
                'affinity' : affinity,
                'origin' : origin,
                'traits' : traits,
                'jutsus' : jutsus,
                'description' : description,
                'avatar' : avatar, 
            }

            prompt = story_character_background_prompt(prompt_data)
            res = generate_json_content(prompt)

            story = res.get('story')
            if not story:
                return JsonResponse({'status':'error', 'message':'Erreur de connection'})
            
            character = {
                'avatar' : avatar,
                'name' : name,
                'PV' : 300,
                'chakra_pool' : 200,
                'stamina_pool' : 9000,
                'rank' : '',
                'jutsus' : jutsus,
                'story' : story
            }

            character_data = {
                'name' : name,
                'gender' : gender,
                'affinity' : affinity,
                'origin' : origin,
                'traits' : traits,
                'jutsus' : jutsus,
                'description' : description,
                'avatar' : avatar, 
                #'coins' : 1200,
                'story' : story
            }

            new_character = StoryCharacter.objects.create(
                player = player,
                character = character,
                character_data = character_data,
            )
            new_character.save()
            player.battle_points -= 1
            player.save()
            return JsonResponse({'status':'success', 'character' : character_data})
        else:
            return JsonResponse({'status':'error', 'message':'Pas Assez de Jetons de Combat'})

    return render(request, "story/create_character.html", {
        "player" : player,
        "n_notifs": get_notifs(player),
        
    })

def characters(request):
    player = get_player(request.user)
    characters = StoryCharacter.objects.filter(player = player)
    characters_data = [ _story_character(ch) for ch in characters ]

    if not characters.exists():
        messages.info(request, "Tu n'as pas encore de personnage. Crée-en un pour commencer ton aventure.")
        return redirect('story:create_character')

    return render(request, "story/characters.html", {
        "player" : player,
        'characters' : characters_data
        
    })

def get_story_status(challenge):
    textpads = StoryTextPad.objects.filter(challenge = challenge )
    if len(textpads) == 0:
        return 'not_started'
    elif challenge.ended:
        return 'ended'
    elif len(textpads) > 0 and textpads.last().text:
        return 'ongoing'
    

def _can_play(player:Player,challenge:StoryChallenge):
    character = challenge.character
    n_texpads = StoryTextPad.objects.filter(challenge = challenge).count()
    story_pass = StoryPass.objects.filter(player = player,challenge = challenge)
    all_pass = StoryPass.objects.filter(player = player, all = True)

    if all_pass.exists():
        return True

    if n_texpads >= 10 and not  story_pass.exists():
        return False
    else:
        return True

 
@csrf_exempt
def subscribe_challenge(request, character_id):
    player = get_player(request.user)
    character = StoryCharacter.objects.get(id = character_id)
    story_challenge,created = StoryChallenge.objects.get_or_create(
        character = character,
    )
    story_challenge.save()  

    if request.method == 'POST':
        subscription = request.POST.get('subscription')
        all = subscription == 'all'
        points = 5500 if all else 2000 
        if player.battle_points >= points:
            story_pass = StoryPass.objects.create(
                    challenge = story_challenge,
                    player = player,
                    all = all)
             
            player.battle_points -= points
            story_pass.save() 
            player.save()
            return JsonResponse({'status':'success', 'message': 'Pass obtenu'}) 
        else:
            return JsonResponse({'status':'error', 'message': 'Pas assez de jetons(JC)'})    
    return JsonResponse({'status':'error', 'message': 'bad request'})     


@login_required
def game(request,character_id):
    player = get_player(request.user)
    character = StoryCharacter.objects.get(id = character_id)
    story_challenge,created = StoryChallenge.objects.get_or_create(
        character = character,
    )
    story_challenge.save() 
    character_data = _story_character(character)
    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
    textpads_data = [  { "text": textpad.text, "entry" : textpad.entry if textpad.entry else "" } for textpad in textpads ]
    story_status = get_story_status(story_challenge)
    status_message = "L'aventure n'a pas encore commencé" if story_status == "not_started" else "L'aventure est  terminé, tu peux en commencer une autre"
    if request.method == "POST":
        if character.player == player:
            action = request.POST.get('action')

            if not _can_play(player,story_challenge):
                return JsonResponse({ 'status' : 'error', 'message' : 'subscription' })

            if action == 'continue':
                if story_status == "ongoing":
                    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
                    textpads_data = [  textpad.text  for textpad in textpads ]
                    prompt = story_continue_prompt(character.character_data, textpads_data)
                    try:
                        res = generate_json_content(prompt)
                        input_required = res.get('input_required') == 'true'
                        text = res.get('text')
                        if not text:
                            return JsonResponse({'status':'error', 'message':'Erreur de connection'})
                        
                        new_textpad = StoryTextPad.objects.create(
                            challenge = story_challenge,
                            text = text
                        )
                        new_textpad.save()

                        return JsonResponse({'status' : 'success', 'input_required':input_required, 'text' : text})
                    except Exception as e:
                        return JsonResponse({'status':'error', 'message':f'Erreur de connection {e}'})
                else:
                    return JsonResponse({'status':'error', 'message' : status_message})

            elif action == 'turn':
                if story_status == "ongoing":
                    text = request.POST.get('text')
                    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
                    textpads_data = [  textpad.text for textpad in textpads ]
                
                    prompt = story_evaluate_and_continue(character.character_data, textpads_data, text)
                    try:
                        res = generate_json_content(prompt)
                        res_text = res.get('text')
                        valid = res.get('valid') == 'true'
                        ended = res.get('ended') == 'true'
                        # print(res_text, valid)
                        if not res_text:
                            return JsonResponse({'status':'error', 'message':'Erreur de connection'})
                        
                        if valid:
                            new_textpad = StoryTextPad.objects.create(
                                challenge = story_challenge,
                                text = res_text,
                                entry = text,
                            )
                            new_textpad.save()
                            if ended:
                                story_challenge.ended = True
                                story_challenge.save()

                            return JsonResponse({'status' : 'success', 'text' : res_text})
                        else:
                            return JsonResponse({'status' : 'success', 'text' : "Tes actions ne sont pas réalisable, tu dois reformuler ta réponse."})
                    except Exception as e:
                        return JsonResponse({'status':'error', 'message':f'Erreur de connection {e}'})
                else:
                    return JsonResponse({'status':'error', 'message' : status_message})


            elif action == 'start':
                if len(textpads) == 0:
                    prompt = story_start_prompt(character.character_data)
                    # print(prompt)
                    res = generate_json_content(prompt)
                    text = res.get('text')

                    if not text:
                        return JsonResponse({'status':'error', 'message':'Request Error'})
                    
                    new_textpad = StoryTextPad.objects.create(
                        challenge = story_challenge,
                        text = text
                    )
                    new_textpad.save()
                    return JsonResponse({'status' : 'success', 'text' : text})
                else:
                    return JsonResponse({'status' : 'error', 'message' : "L'aventure a déja debuté."})
        else:
            return JsonResponse({'status' : 'error', 'message' : "Action non autorisée."})



    return render(request, "story/game.html", {
        "player" : player,
        'character' : character_data,
        "textpads" : textpads_data,
        'status' : story_status,
        "n_notifs" : get_notifs(player),
    })

@csrf_exempt
def array_test(request):
    if request.method == "POST":
        jutsus = request.POST['jutsus']
        jutsus = str(jutsus).replace('[','').replace(']','')
        print(jutsus)
        jutsus_list = [j.strip() for j in jutsus.split(',')] if jutsus else [] 
        print(jutsus_list)
        return JsonResponse({'jutsus':jutsus})
