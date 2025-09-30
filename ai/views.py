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
import os
import json
import base64
from google.oauth2 import service_account
import vertexai
import tempfile

from google.genai.types import GenerateContentConfig, Modality,Part
from PIL import Image
from io import BytesIO
from django.utils import timezone
load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') 
BASE_DIR = Path(__file__).resolve().parent




# # Check if the raw JSON content is available in an environment variable
# if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
#     credentials_json_base64 = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
#     try:
#         # Decode if it was Base64 encoded
#         credentials_json_bytes = base64.b64decode(credentials_json_base64)
#         credentials_info = json.loads(credentials_json_bytes)
#     except Exception:
#         # If not Base64 encoded, assume it's raw JSON
#         credentials_info = json.loads(credentials_json_base64)

#     credentials = service_account.Credentials.from_service_account_info(credentials_info)
#     print("Authenticated using JSON content from environment variable.")

# # If the JSON content environment variable is not set, fall back to GOOGLE_APPLICATION_CREDENTIALS
# # This is for local development if you still want to use the file path
# elif "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
#     credentials_path = os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
#     credentials = service_account.Credentials.from_service_account_file(credentials_path)
#     print(f"Authenticated using file path from GOOGLE_APPLICATION_CREDENTIALS: {credentials_path}")
# else:
#     # Fallback for when no credentials are explicitly provided (might use default ADC)
#     # This might not work in all scenarios, depending on your setup
#     credentials = None # Or raise an error, or attempt default application credentials
#     print("No explicit Google Cloud credentials found. Attempting default application credentials.")

# Now you can use 'credentials' to initialize your Google Cloud client
# For example, with Google Cloud Storage:
# client = storage.Client(credentials=credentials)

def authenticate_genai_with_service_account():
    """
    Authenticates genai for Vertex AI using a service account JSON 
    stored in an environment variable.
    """
    if "GOOGLE_APPLICATION_CREDENTIALS_JSON" in os.environ:
        credentials_json_base64 = os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"]
        try:
            # Decode if it was Base64 encoded
            credentials_json_bytes = base64.b64decode(credentials_json_base64)
            credentials_info = json.loads(credentials_json_bytes)
        except Exception:
            # If not Base64 encoded, assume it's raw JSON
            credentials_info = json.loads(credentials_json_base64)

        # Create a temporary file for the service account key
        # This is crucial because google.auth expects a file path
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_key_file:
            json.dump(credentials_info, temp_key_file)
            temp_file_path = temp_key_file.name

        # Set GOOGLE_APPLICATION_CREDENTIALS to the path of the temporary file
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_file_path
        print(f"Temporary service account file created at: {temp_file_path}")

        # Important: Initialize Vertex AI. This will pick up GOOGLE_APPLICATION_CREDENTIALS
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        location = os.getenv("GOOGLE_CLOUD_LOCATION")

        if not project_id or not location:
            raise ValueError("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set when using Vertex AI.")

        vertexai.init(project=project_id, location=location)
        print(f"Vertex AI initialized for project: {project_id}, location: {location}")

        # Now, the genai client can be initialized for Vertex AI
        # It will automatically use the credentials set via GOOGLE_APPLICATION_CREDENTIALS
        # client = genai.GenerativeModel('gemini-pro', 
        #                              # The vertexai=True parameter is often inferred if vertexai.init is called
        #                              # but explicitly setting it can be good for clarity.
        #                              # The client will also pick up project/location from vertexai.init()
        #                              # You can also pass them explicitly here if not using vertexai.init()
        #                              # vertexai=True, project=project_id, location=location
        #                             )
        client =  genai.Client(http_options= HttpOptions(api_version='v1'))

        print("GenAI client initialized for Vertex AI.")
        return client, temp_file_path # Return temp_file_path so it can be cleaned up
    else:
        print("GOOGLE_APPLICATION_CREDENTIALS_JSON not found. Falling back to default ADC or API key.")
        # Fallback for local development or if using API key
        # If GOOGLE_APPLICATION_CREDENTIALS is set locally, it will be used
        # Otherwise, it might try to use GOOGLE_API_KEY or default ADC
        try:
            # # This will try to use GOOGLE_API_KEY if set, or ADC if available
            # if os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "True":
            #      project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            #      location = os.getenv("GOOGLE_CLOUD_LOCATION")
            #      if not project_id or not location:
            #          raise ValueError("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set when using Vertex AI.")
            #      vertexai.init(project=project_id, location=location)
            #      client = genai.GenerativeModel('gemini-pro')
            # else:
            #     client = genai.GenerativeModel('gemini-pro')
            # return client, None
            client =  genai.Client(http_options= HttpOptions(api_version='v1'))
            return client,None
        except Exception as e:
            print(f"Could not initialize GenAI client without explicit credentials: {e}")
            return None, None



# client =  genai.Client(http_options= HttpOptions(api_version='v1'), credentials = credentials)
client, temp_file = authenticate_genai_with_service_account()

def generate_image(prompt, file_name= f"generated-image", reference_img=None):
    print(prompt)
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=(
            prompt,
            Part.from_uri(
                file_uri=reference_img,
                mime_type='image/png' if reference_img else None
            ) if reference_img else " "
        ),
        config=GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE]),
    )
    images = []
    for part in response.candidates[0].content.parts:
        if part.text:
            print(part.text)
        elif part.inline_data:
            # file_path = f"media/generated_images/{file_name}-{random.randint(1000,99999)}.png"
            file_path = f"media/{file_name}-{random.randint(1000,99999)}.png"
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(file_path)
            images.append(
                {
                    # "image" : image,
                    "path" : file_path
                }
            )
    return images  


    

def generate_avatar_images(request):
    player = get_object_or_404(Player, user = request.user) 
    if request.method == "POST" and player:
        gender = request.POST.get('gender')
        description = request.POST.get('description')
        prompt = f"""
        generate two images of character avatar ideas for an adventure roleplaying game in the naruto verse.
        gender is {gender}, basic description is {description}.
        Each image should show atleast half of the body of the avatar, on every image, only one avatar should be represented so that 
        the player will be able to chose the one that he/she prefers
        """
        try:
            images = generate_image(prompt = prompt, file_name="story-avatar")
        except Exception as e:
            print(e)
            return JsonResponse({'status':'error', 'message':f'{e}'})    
        
        return JsonResponse({'status':'success', 'images':images})
    return JsonResponse({'status':'error'})  

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
    if request.method == "POST" and player:
        battle = get_object_or_404(Battle, id = battle_id)
        prompt = set_rules_prompt(battle.i_character, battle.o_character, battle.type)


        #response = ask_gemini(prompt)
        

        #credentials = load_credentials_from_file("E:\work\\alex\google\secure_keys\\roleplay-verse-5163419666ba.json")
        #client = genai.Client(http_options=HttpOptions(api_version='v1'), credentials=credentials)
        if battle.ai_refereeing and not battle.ai_rules and player in [battle.initiator, battle.opponent, battle.refree]:
            try:
                response = client.models.generate_content(
                model = "gemini-2.0-flash-001",
                contents = prompt,
                )
            except Exception as e:
                print(f"Error generating content: {e}")
                return JsonResponse({'status':'error', 'message':'Erreur lors de la génération des règles, réessayez plus tard.'})
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Cleaned up temporary service account file: {temp_file}")    
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

def generate_json_content(prompt):
    try:
        response = client.models.generate_content(
        model = "gemini-2.0-flash-001",
        contents = prompt,
        )
        # print(response)
        response_string = str(response.text).replace("```json", "").replace("```", "").strip()    
        # print(response_string)
        ai_response = json.loads(response_string)
        # print(ai_response)
        return ai_response
    except Exception as e:
        print(f"Error generating content: {e}")
        return {'status':'error', 'message':'Erreur lors de la génération du text, réessayez plus tard.'}  
    finally:
        if temp_file and os.path.exists(temp_file):
            os.remove(temp_file)
            print(f"Cleaned up temporary service account file: {temp_file}")

def make_verdict(request, battle_id):
    player = get_player(request.user)
    if request.method == "POST":
        battle = get_object_or_404(Battle, id = battle_id)
        if battle.ai_refereeing and not battle.can_send_textpad and battle.status == 'ongoing' and player in [battle.initiator, battle.opponent]:
            textpads = TextPad.objects.filter(battle = battle).order_by('date_sent')
            last_textpad = textpads.last()
            if last_textpad.refree_comment:
                return JsonResponse({'status':'error', 'message':'Déja Evalué'})
            character = battle.i_character if last_textpad.owner == battle.initiator else battle.o_character
            context = _battle_context(battle)
            print(context)
            hidden_actions = _get_hidden_actions(battle)
            textpads_data = " \n".join([
                f"""
                personnage : {battle.i_character if textpad.owner == battle.initiator else battle.o_character},
                déscription de l'action : {textpad.text},
                Action cachée : {textpad.hidden_action if textpad.hidden_action else "Aucune action cachée dans cette action"},
                evaluation de l'action  : {textpad.refree_comment if textpad.refree_comment else "Le pavé n'a pas encore été evalué"}
                """   
                for  textpad in textpads
            ])
            prompt = battle_verdict_prompt(battle.ai_rules, context, character, last_textpad.text, battle, hidden_actions=hidden_actions, actions = textpads_data)
            try:
                response = client.models.generate_content(
                model = "gemini-2.0-flash-001",
                contents = prompt,
                )
            except Exception as e:
                print(f"Error generating content: {e}")
                return JsonResponse({'status':'error', 'message':'Erreur lors de la génération du verdict, réessayez plus tard.'})    
            finally:
                if temp_file and os.path.exists(temp_file):
                    os.remove(temp_file)
                    print(f"Cleaned up temporary service account file: {temp_file}")
            # try:
            response_string = str(response.text).replace("```json", "").replace("```", "").strip()    
            ai_response = json.loads(response_string)
            verdict = ai_response.get('verdict')
            validity = ai_response.get('valid') == "true"
            end_fight = ai_response.get('end_fight') == "true"
            last_textpad.valid = validity
            last_textpad.date_validated = timezone.now()
            last_textpad.refree_comment = verdict
            last_textpad.save()
            
            print(ai_response)
            
            #set the possibility to send a new text pad if the last one is valid 
            # battle.can_send_textpad = validity
            battle.can_send_textpad = not end_fight
            if end_fight: 
                
                print('fight is ended')
                winner_character:str = ai_response.get('winner')
                print(f"Winner character: {winner_character}")
                winner = battle.initiator if winner_character.strip().lower() == battle.i_character.strip().lower() else battle.opponent
                loser = battle.opponent if winner == battle.initiator else battle.initiator
                #loser = last_textpad.owner
                #winner = battle.initiator if loser == battle.opponent else battle.opponent
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
                print("updating player's family points...")
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
