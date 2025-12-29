from django.shortcuts import get_object_or_404, redirect, render
from api.models import PushSubscription
from api.utility import send_push_notification
from core.models import Notification
from store.models import AffiliateProduct
from store.views import affiliate_product_data
from users.models import Player
from users.users_utility import get_player
from ai.views import generate_image, generate_json_content
from ai.prompts import story_character_background_prompt, story_continue_prompt, story_evaluate_and_continue, story_image_generation_prompt, story_start_prompt
from utility import _time_since
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
from users.views import _player_data 

LANGUAGES = {
        'fr' : 'Francais',
        'en' : 'Anglais',
    }

def get_bowser_language(request):
    player = get_player(request.user)
    language = request.META.get('HTTP_ACCEPT_LANGUAGE','fr')[:2].lower()
    print(language,request.META.get('HTTP_ACCEPT_LANGUAGE'))
    
    if player:
        player.language = language
        player.save()
    return language
    

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
    data['feed_item'] = 'story'
    data['story'] = ch.get('story')
    data['affinity_icon'] = getAffinityIcon(data.get('affinity'))
    data['player'] = _player_data(character.player)
    data['last_entry'] = ""
    
    challenge = StoryChallenge.objects.filter(character = character).first()
    last_textpad = StoryTextPad.objects.filter(challenge = challenge).last()
    data['reads'] = challenge.reads + challenge.readers.count() + 10
    if last_textpad:
        data['last_textpad'] = last_textpad.text
        data['last_entry'] = last_textpad.entry if last_textpad.entry else ""
    else:
        data['last_textpad'] = ch.get('story')    

    return data

def _story_data(story:StoryChallenge):
    character = _story_character(story.character)
    data = {
        'character_id' : story.character.id,
        'character' : character,
        'title' : character['name'],
        'cover' : character['avatar'],
        'author' : character['player'],
        'summary' : StoryTextPad.objects.filter(challenge = story).first().text if StoryTextPad.objects.filter(challenge = story).first() else character['description'],
        'readers_count' : story.readers.all().count(),

    }

    return data

def index(request):
    player = get_player(request.user)
    top_stories= [ _story_data(story) for story in StoryChallenge.objects.order_by('?')[:5]]
    return render(request, "story/index.html", {
        "player" : player,
        "best_stories" : top_stories
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
        isShinobi = request.POST.get('isShinobi') == 'true'
        language = LANGUAGES.get(get_bowser_language(request), 'Francais')
        
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

            prompt = story_character_background_prompt(prompt_data, isShinobi,language)
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

    if player != character.player:
        return False

    if all_pass.exists():
        return True

    if n_texpads >= FREE_TEXTPAD_LIMIT and not  story_pass.exists():
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
        points = ALL_PASS if all else BASIC_PASS
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

def remove_ads(request):
    player = get_player(request.user)

    if request.method == "POST":
        if player.battle_points >= NO_ADS_PASS:
            NoAdsPass.objects.create(player = player)
            player.battle_points -= NO_ADS_PASS 
            player.save()
            return JsonResponse({'status':'success', 'message': 'Publicité supprimée'}) 
        else:
            return JsonResponse({'status':'error', 'message': 'Pas assez de jetons(JC)'})

    return JsonResponse({'status':'error', 'message': 'bad request'})

def generate_scene_images(character:StoryCharacter,  textpads):
    scene_description_prompt = story_image_generation_prompt(character.character_data, textpads[-1])
    scene_description = generate_json_content(scene_description_prompt).get('description')
    print(scene_description)
    illustration_generation_prompt = f"""
                        Ca c'est le personnage principale {character.character_data.get('name')}. pas de modification bizarre de ses cheveux ou autres aspects physique.
                        Genere deux Illustrations de style concept art d'anime Naruto de haute qualité, avec des contours nets et un ombrage lisse suivant la description donné ci-dessous. chaque image doit etre une vu de la scene sous un angle different:
                        {scene_description}
                        """
    images = generate_image(illustration_generation_prompt, reference_img="gs://rpv-story-avatars/alpha.png") if scene_description else []
    print(images)
    return images

def _story_textpad_data(textpad:StoryTextPad):
    data = { 
        "id": textpad.id, 
        "text": textpad.text,
        "entry" : textpad.entry if textpad.entry else "",
        'reactions' : textpad.reactors.all().count(),
        'comments' : StoryTextPadComment.objects.filter(textpad = textpad).count(),
        'most_reaction' : textpad.most_made_reaction()['type'] if textpad.most_made_reaction() else '👍',
        "images": textpad.data.get('images',[]) if textpad.data else [] }
    
    return data

def game(request,character_id):
    player = get_player(request.user)
    character = StoryCharacter.objects.get(id = character_id)
    story_challenge,created = StoryChallenge.objects.get_or_create(
        character = character,
    )
    story_challenge.reads += 1
    story_challenge.save() 
    
    character_data = _story_character(character)
    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
    textpads_data = [  _story_textpad_data(textpad) for textpad in textpads ]
    story_status = get_story_status(story_challenge)
    status_message = "L'aventure n'a pas encore commencé" if story_status == "not_started" else "L'aventure est  terminé, tu peux en commencer une autre"
    show_ads = not(NoAdsPass.objects.filter(player = player).exists() or StoryPass.objects.filter(player = player, all = True).exists())
    affiliate_products = [  affiliate_product_data(product) for product in AffiliateProduct.objects.order_by("?") ] 

    if request.method == "POST":
        if character.player == player:
            action = request.POST.get('action')
            language = LANGUAGES.get(get_bowser_language(request), 'Francais')

            if not _can_play(player,story_challenge):
                return JsonResponse({ 'status' : 'error', 'message' : 'subscription' })

            if action == 'continue':
                if story_status == "ongoing":
                    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
                    textpads_data = [  textpad.text  for textpad in textpads ]
                    prompt = story_continue_prompt(character.character_data, textpads_data, language)
            
                    try:
                        res = generate_json_content(prompt)
                        scene_illustrations =  [] #generate_scene_images(character, textpads_data)
                        data = {
                            'images' : scene_illustrations
                        }  
                        input_required = res.get('input_required') == 'true'
                        text = res.get('text')
                        if not text:
                            return JsonResponse({'status':'error', 'message':'Erreur de connection'})

                        data = {
                            'images' : scene_illustrations
                        }
                        new_textpad = StoryTextPad.objects.create(
                            challenge = story_challenge,
                            text = text,
                            data = data
                        )
                        new_textpad.save()

                        return JsonResponse({'status' : 'success', 'input_required':input_required, 'textpad' : _story_textpad_data(new_textpad), 'images': scene_illustrations})
                    except Exception as e:
                        return JsonResponse({'status':'error', 'message':f'Erreur de connection {e}'})
                else:
                    return JsonResponse({'status':'error', 'message' : status_message})

            elif action == 'turn':
                if story_status == "ongoing":
                    text = request.POST.get('text')
                    textpads = StoryTextPad.objects.filter(challenge = story_challenge)
                    textpads_data = [  textpad.text for textpad in textpads ]
                
                    prompt = story_evaluate_and_continue(character.character_data, textpads_data, text, language)
                    try:
                        res = generate_json_content(prompt)
                        res_text = res.get('text')
                        valid = res.get('valid') == 'true'
                        ended = res.get('ended') == 'true'
                        # print(res_text, valid)
                        if not res_text:
                            return JsonResponse({'status':'error', 'message':'Erreur de connection'})

                        scene_illustrations = [] #generate_scene_images(character, textpads_data)
                        data = {
                            'images' : scene_illustrations
                        }    
                        
                        if valid:
                            new_textpad = StoryTextPad.objects.create(
                                challenge = story_challenge,
                                text = res_text,
                                entry = text,
                                data = data
                            )
                            new_textpad.save()
                            if ended:
                                story_challenge.ended = True
                                story_challenge.save()

                            return JsonResponse({'status' : 'success', 'textpad' : _story_textpad_data(new_textpad)})
                        else:
                            return JsonResponse({'status' : 'success', 'text' : "Tes actions ne sont pas réalisable, tu dois reformuler ta réponse.",'images' : scene_illustrations})
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
                    return JsonResponse({'status' : 'success', 'textpad' : _story_textpad_data(new_textpad)})
                else:
                    return JsonResponse({'status' : 'error', 'message' : "L'aventure a déja debuté."})
        else:
            return JsonResponse({'status' : 'error', 'message' : "Action non autorisée."})



    return render(request, "story/game.html", {
        "player" : player,
        'can_play' : _can_play(player,story_challenge),
        'character' : character_data,
        "textpads" : textpads_data,
        'status' : story_status,
        'basic_pass' : BASIC_PASS,
        'all_pass' : ALL_PASS,
        'no_ads_pass' : NO_ADS_PASS,
        'show_ads' : show_ads,
        'affiliate_products' : affiliate_products,
    })

def _story_textpad_reactions_data(textpad_reactor:StoryTextpadReactor):
    return {
        'date_added' : _time_since(textpad_reactor.date_added),
        'reaction' : textpad_reactor.type,
        'player' : textpad_reactor.player.user.username,
    }

def _story_textpad_comment_data(comment:StoryTextPadComment):
    data:dict = {    
                "textpad_id" : comment.textpad.id,
                "id": comment.id,
                "text": comment.text,
                'body_full': comment.text,
                'body': comment.text[:197]+'...' if len(comment.text) > 200 else comment.text,
                "author": {
                    'id' : comment.author.id,
                    "player": str(comment.author),
                    "username": comment.author.user.username,
                    'profile_picture' : comment.author.profile_picture.url,
                },
                'parent' : {
                    "id": comment.parent.id,
                    "author": {
                        "id": comment.parent.author.id,
                        "username": comment.parent.author.user.username,
                        "player": str(comment.parent.author),
                        "profile_picture": comment.parent.author.profile_picture.url,
                    },
                    # "body_full" : comment.text,
                    # "body": comment.parent.text[:50] + '...' if len(comment.parent.text) > 50 else comment.parent.text,
                } if comment.parent else None,
                "timestamp":  _time_since(comment.date_added),
                'likes' : 0,
                'replies' : [ _story_textpad_comment_data(reply) for reply in StoryTextPadComment.objects.filter(parent = comment).order_by("date_added") ],
                #'is_reply' : TextPadComment.objects.filter(parent = ).exists()
            },
    
    
    return data 

def react_to_story_textpad(request, textpad_id):
    textpad = get_object_or_404(StoryTextPad, id = textpad_id)
    player = get_player(request.user)

    if request.method == 'POST':
        
        reaction = request.POST.get('reaction','😂')
        
        reactors = textpad.reactors.all()

        if player in reactors:
            player_reaction = StoryTextpadReactor.objects.get(player = player, textpad = textpad)
            if reaction == player_reaction.type:
                textpad.reactors.remove(player)
            else:
                player_reaction.type = reaction  
                player_reaction.save()      
        else:
            textpad.reactors.add(player, through_defaults={'type': reaction})
            if player == textpad.challenge.character.player:
                new_notif = Notification.objects.create(
                        target = textpad.challenge.character.player,
                        url = f'/story/game/{textpad.challenge.id}',
                        content = f"{player} a reagi a un pavé dans ta story",
                        img_url = player.profile_picture.url
                    )
                new_notif.save()
                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = textpad.challenge.character.player.user).last(),
                    {
                    'title' : f"Nouvelle reaction sur ton pavé",
                    'body' : f"{player} a reagi par '{reaction}' a un pavé dans ta story",
                    'url' : f'/story/game/{textpad.challenge.id}',
                    'icon' : player.profile_picture.url,
                    },
                    
                )

        textpad.save()
        reactions = [ _story_textpad_reactions_data(reactor) for reactor in StoryTextpadReactor.objects.filter(textpad = textpad)]

        return JsonResponse({'status':'success', 'reactions': reactions})

def story_textpad_reactors(request, textpad_id):
    textpad = get_object_or_404(StoryTextPad, id = textpad_id)
    reactors = StoryTextpadReactor.objects.filter(textpad = textpad)
    players = [] 
    for reactor in reactors :
        data = _player_data(reactor.player) 
        data['reaction'] = reactor.type
        players.append(data)

    return JsonResponse({'status':'success', 'reactors': players})    


def add_story_textpad_comment(request, textpad_id):
    if request.method == 'POST':
        textpad = get_object_or_404(StoryTextPad, id=textpad_id)
        author = get_player(request.user)  # Assuming Player is linked to User
        text = request.POST.get("body")
        parent_id = request.POST.get("parent_id")

        parent = None
        if parent_id:
            parent = get_object_or_404(StoryTextPadComment, id=parent_id)

        comment = StoryTextPadComment.objects.create(
            textpad=textpad, author=author, text=text, parent=parent
        )
        comment.save()

        if comment.author != textpad.challenge.character.player:
            if comment.parent:
                if comment.parent.author != comment.author:
                    new_notif = Notification.objects.create(
                        target = comment.parent.author,
                        url = f'/story/game/{textpad.challenge.id}',
                        content = f"{comment.author} a repondu a ton commentaire sur un pavé",
                        img_url = comment.author.profile_picture.url
                    )
                    new_notif.save()
                    #send push notification to the opponent and the referee
                    send_push_notification(
                        PushSubscription.objects.filter(user = comment.parent.author.user).last(),
                        {
                        'title' : f"Nouvelle reaction sur ton pavé",
                        'body' : f"{comment.author} a repondu a ton commentaire sur un pavé",
                        'url' : f'/story/game/{textpad.challenge.id}',
                        'icon' : '/static/images/logo/logo_1.png',
                        },
                        
                    )
            else:
                new_notif = Notification.objects.create(
                    target = textpad.challenge.character.player,
                    url = f'/story/game/{textpad.challenge.id}',
                    content = f"{comment.author} a commenté ton pavé dans un combat",
                    img_url = comment.author.profile_picture.url
                )
                new_notif.save()
                #send push notification to the opponent and the referee
                send_push_notification(
                    PushSubscription.objects.filter(user = textpad.challenge.character.player.user).last(),
                    {
                    'title' : f"Nouvelle reaction sur ton pavé",
                    'body' : f"{comment.author} a repondu a ton commentaire sur un pavé",
                    'url' : f'/story/game/{textpad.challenge.id}',
                    'icon' : comment.author.profile_picture.url,
                    },
                    
                )

                
                
        return JsonResponse({
            "status": "success",
            "comment": _story_textpad_comment_data(comment)
        })


def get_story_textpad_comments(request, textpad_id):
    textpad = get_object_or_404(StoryTextPad, id=textpad_id)
    comments = StoryTextPadComment.objects.filter(parent=None, textpad = textpad).order_by("-date_added")
    data = [_story_textpad_comment_data(comment) for comment in comments]
    
    return JsonResponse({ 'status': 'success', 'comments' : data}, safe=False)  

@csrf_exempt
def array_test(request):
    if request.method == "POST":
        jutsus = request.POST['jutsus']
        jutsus = str(jutsus).replace('[','').replace(']','')
        print(jutsus)
        jutsus_list = [j.strip() for j in jutsus.split(',')] if jutsus else [] 
        print(jutsus_list)
        return JsonResponse({'jutsus':jutsus})
