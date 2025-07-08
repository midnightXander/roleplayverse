from datetime import datetime
from django.shortcuts import get_object_or_404, redirect, render
from api.models import PushSubscription
from api.utility import send_push_notification
from battles.models import SoloBattle
from battles.views import player_progress, update_points, update_rank
import core.models as core_models
from users.models import Player
from utility import _solo_battle_character, get_solo_battle_characters
from .models import *
from battles.models import *
import json, random
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from pathlib import Path
import os
import json
from google import genai
from google.genai.types import HttpOptions
from google.auth import load_credentials_from_file
from dotenv import load_dotenv
from .vertex_ai import ask_gemini
from .prompts import *
from users.users_utility import get_player
import events.views as events_views
load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') 


BASE_DIR = Path(__file__).resolve().parent

client =  genai.Client(http_options= HttpOptions(api_version='v1'))


def enable_ai_refreeing(request, battle_id):
    player = get_object_or_404(Player, user = request.user) 
    if request.method == "POST":
        battle = Battle.objects.get(id = battle_id)

        message = ''
       
        battle.status = battle_status[1]
        battle.ai_refereeing = True
        new_notif = core_models.Notification.objects.create(
            target = battle.initiator,
            content = f"ton combat contre {battle.opponent} est prét a commencé avec l'arbitrage IA, clique pour aller générer les regles du combat ",
            url = f'/battles/battle_room/{battle.id}',
        ) 
        new_notif2 = core_models.Notification.objects.create(
            target = battle.opponent,
            content = f"{player} a activé l'arbitrage IA sur votre combat {battle.i_character} vs {battle.o_character}, tu peux desormais generer les regles du combat",
            url = f'/battles/battle_room/{battle.id}',
        ) 
        new_notif.save() 
        new_notif2.save()

        send_push_notification(
            PushSubscription.objects.filter(user = battle.opponent.user).last(),
            {
            'title' : f"Ton combat peut Commencer",
            'body' : f"{player} a activé l'arbitrage IA sur votre combat {battle.i_character} vs {battle.o_character}, tu peux desormais generer les règles du combat et envoyer ton pave",
            'url' : f'/battles/battle_room/{battle.id}',
            'icon' : '/static/images/logo/logo_1.png',
            },
            
        )

        send_push_notification(
            PushSubscription.objects.filter(user = player.user).last(),
            {
            'title' : f"Proposition d'arbitrage acceptée",
            'body' : f"Ta proposition d'arbitrer le combat {battle.initiator} vs {battle.opponent} a été accepté, tu dois a présent mettre en place les régles du combat",
            'url' : f'/battles/battle_room/{battle.id}',
            'icon' : '/static/images/logo/logo_1.png',
            },
            
        )

        battle.save()
        new_notif.save()
        message = "Arbitre IA activé, tu peux maintnenant generer les règles"
        return JsonResponse({"status":"success","message": message})
        
    return JsonResponse({"status":"failed","message":message})

def create_rules(request, battle_id):
    player = get_player(request.user)
    if request.method == "POST":
        battle = get_object_or_404(Battle, id = battle_id)
        prompt = set_rules_prompt(battle.i_character, battle.o_character, battle.type)


        #response = ask_gemini(prompt)
        

        #credentials = load_credentials_from_file("E:\work\\alex\google\secure_keys\\roleplay-verse-5163419666ba.json")
        #client = genai.Client(http_options=HttpOptions(api_version='v1'), credentials=credentials)
        if battle.ai_refereeing and not battle.ai_rules:
            
            response = client.models.generate_content(
            model = "gemini-2.0-flash-001",
            contents = prompt,
            )
            battle.ai_rules = response.text
            battle.can_send_textpad = True
            battle.save()

            notif_target = battle.initiator if player == battle.opponent else battle.opponent
            notif1 = core_models.Notification.objects.create(
                target = notif_target,
                content = f"les règles de ton combat ont été fixé par IA. Le premier pavé peut etre envoyé.",
                url = f'/battles/battle_room/{battle.id}',
            )
            
            notif1.save()
            send_push_notification(
                PushSubscription.objects.filter(user = notif_target.user).last(),
                {
                'title' : f"Les régles de ton combat ont été fixées",
                'body' : f"les règles de ton combat ont été fixé par IA. Le premier pavé peut etre envoyé",
                'url' : f'/battles/battle_room/{battle.id}',
                'icon' : '/static/images/logo/logo_1.png',
                },
            )

            return JsonResponse({'status':'success', 'response':response.text})
        else:
            return JsonResponse({'status':'error', 'message':"Les Regles ont deja ete etablie"})

    return JsonResponse({'status':'error', 'message':'bad request',})

def _battle_context(battle:Battle):
    textpads = TextPad.objects.filter(battle = battle)
    if textpads.count() <= 1:
        return "Le combat vient de debuter, aucune action precedente"
    else:
        context = """ """
        for textpad in textpads:
            context += f"""  {textpad.refree_comment}\n """ 
            # return [f"""  {textpad.refree_comment}\n """ for textpad in textpads ]
        return context           

def _get_hidden_actions(battle:Battle):
    textpads = TextPad.objects.filter(battle = battle)
    if textpads.count() <= 1:
        return None
    else:
        actions = []
        for textpad in textpads:
            if textpad.hidden_action:
                actions.append(
                    f"""
                        "personnage" : {battle.i_character if textpad.owner == battle.initiator else battle.o_character},
                        "action cachée" : {textpad.hidden_action}
                    """
                   )
        return "\n".join(actions) if actions else None

def make_verdict(request, battle_id):
    player = get_player(request.user)
    if request.method == "POST":
        battle = get_object_or_404(Battle, id = battle_id)
        if battle.ai_refereeing and not battle.can_send_textpad and battle.status == 'ongoing' and player in [battle.initiator, battle.opponent]:
            textpads = TextPad.objects.filter(battle = battle)
            last_textpad = textpads.last()
            if last_textpad.refree_comment:
                return JsonResponse({'status':'error', 'message':'Déja Evalué'})
            character = battle.i_character if last_textpad.owner == battle.initiator else battle.o_character
            context = _battle_context(battle)
            print(context)
            hidden_actions = _get_hidden_actions(battle)
            
            prompt = battle_verdict_prompt(battle.ai_rules, context, character, last_textpad.text, battle, hidden_actions=hidden_actions)
            response = client.models.generate_content(
            model = "gemini-2.0-flash-001",
            contents = prompt,
            )
            # try:
            response_string = str(response.text).replace("```json", "").replace("```", "").strip()    
            ai_response = json.loads(response_string)
            verdict = ai_response.get('verdict')
            validity = ai_response.get('end_fight') == "false"
            last_textpad.valid = validity
            last_textpad.date_validated = timezone.now()
            last_textpad.refree_comment = verdict
            last_textpad.save()
            
            
            #set the possibility to send a new text pad if the last one is valid 
            battle.can_send_textpad = validity
            if not validity : 
                print('fight is ended')
                loser = last_textpad.owner
                winner = battle.initiator if loser == battle.opponent else battle.opponent
                win_notif = core_models.Notification.objects.create(
                target = winner,
                url = f'/battles/battle_room/{battle.id}',
                content = "Tu as été declaré vainqueur du combat"
                ) 
                win_notif.save()

                send_push_notification(
                    PushSubscription.objects.filter(user = winner.user).last(),
                    {
                    'title' : f"Tu as été declaré vainqueur du combat",
                    'body' : f"Tu as été declaré vainqueur du combat",
                    'url' : f'/battles/battle_room/{battle.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },   
                )
                
                battle.winner = winner 
                battle.status = battle_status[3]
                battle.date_ended = datetime.now()
                battle.defeat_motif =  'referee decision'

                progress =  player_progress(battle=battle,loser_rank = loser.rank)
                winner.progression +=  progress
                
                #update the player's rank if progression reached 100%
                update_rank(winner)
                update_points(family = winner.family, battle=battle, member_progress=progress)
                winner.award_credits(40)

                winner.save()
                battle.save()
                    
                if(battle.type == 'tournament'):
                    events_views._update_round(battle)

                
            else:

                notif_target = battle.opponent if player == battle.initiator else battle.initiator 
                notif1 = core_models.Notification.objects.create(
                    target = notif_target,
                    content = f"Le verdict a été donné sur un de tes combats par Benimaru. Voila ce qu'il en est",
                    url = f'/battles/battle_room/{battle.id}',
                )
                
                notif1.save()
                send_push_notification(
                    PushSubscription.objects.filter(user = notif_target.user).last(),
                    {
                    'title' : f"Le verdict a été donné.",
                    'body' : f"Le verdict a été donné sur un de tes combats par Benimaru. Voila ce qu'il en est",
                    'url' : f'/battles/battle_room/{battle.id}',
                    'icon' : '/static/images/logo/logo_1.png',
                    },
                )
            battle.save()
            last_textpad.save()
            return JsonResponse({'status':'success', 'response':verdict})
            # except:
            #     return JsonResponse({'status':'error', 'message':'Erreur de reponse'})
