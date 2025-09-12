import base64
import json
import tempfile
from google import genai
from google.genai.types import HttpOptions
from dotenv import load_dotenv
import os
from google.genai.types import GenerateContentConfig, Modality,Part
from PIL import Image
from io import BytesIO
import vertexai
import random
from django.utils import timezone
from datetime import datetime
load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') 

# client =  genai.Client(http_options= HttpOptions(api_version='v1'), api_key=api_key)
# response = client.models.generate_content(
#     model = "gemini-2.0-flash-001",
#     contents = "Quels sont les points forts de Naruto dans l'anime naruto shippuden ",
# )
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


def ask_gemini(prompt, model = "gemini-2.0-flash-001"):
    client =  genai.Client(http_options= HttpOptions(api_version='v1'), api_key=api_key)
    response = client.models.generate_content(
    model = "gemini-2.0-flash-001",
    contents = prompt,
    )
    
    return response.text

battle_summary_prompt = [
    "Tu es un arbitre expert de Combat Roleplay autour de l'univers Naruto. Tu dois generer un resumé de moins de 150 mots des actions effectué dans un combat de roleplay naruto depuis les actions decrites ci-dessous.",
    """

    """,
    """

    """,
]

textpad_verdict_prompt = [
    """Tu es un arbitre de Combat Roleplay autour de l'univers Naruto. Tu dois analyser les actions des joueurs decrits dans leurs textes appeler Pavé en fonction des capacités des personnages incarné, des regles du combats et produire un verdict bref de moins de 150 mots contenant un resumer de l'action, des precisions quant a la faisabilite de l'action , de l'etat generale actuel du combat et si le combat peut continuer  en passant a l'action suivante. Tu recevra l'etat actuel du combat ainsi que le contexte. Retourne la reponse en format JSON : { "end_fight":"true"/"false", "verdict":"Ton verdict et le reste des infos que j'ai demander" }  pour pouvoir utliser ta reponse pour mettre a jour l'etat du combat dans ma base de donnees. sachant que 'end_fight' sera 'false' si le combat peut continuer.""",
    """ REGLES: 
    ❖ Le terrain sera un vaste terrain comme celui vue lors du combat de l'alliance sans moindre obstacle aux alentours. 
    ━ Un maximum de seulement trois jutsu est autorisé dans un pavé, les actions cachées seront comptabilisées au tour réalisé. 
    ━ les techniques de permutation et substitution sont formellement interdites.
    ━ les techniques de déplacement instantanée ainsi que toutes actions de déplacement dites instantanée seront utilisables une fois chaque trois tours sur une distance de quinze mètres.
    
    Restrictions ⎾ Sasuke ⏌:
    — 02 clones 
    — Genjutsu visuel sur une portée de 15m. 
    — Shinra et Banshô utilisable une fois chaque deux tours sur une portée de 15m.
    — Gakidô utilisable une fois chaque trois tours, forme une sphère d’un mètre de diamètre.
    — Chikabu donne droit à un seul noyau au 3eme tour sur 15m max à partir de Sasuke. usage unique   
    — Amenotejikara une fois chaque trois tours sur une portée 15m (échange, téléportation).
    — Les autres voies du rinnegan y compris Gedo et les barres noires seront prohibées.
    — Susanô du cage thoracique au complet disponible dès le debut dure 3 tours réutilisables apres 3 tours 
    — Susanôo parfait dure trois tours usage unique
    — Amaterasu et ses variantes utilisable chaque  trois tours  sur une portée de 15m ( porté exclu pour les projectiles de enton) 
    — Kirin se fera en deux tours de préparation suivant les préparations vu dans l'animé usage unique 
    — portail utilisable une fois chaque 4 tour. L'ouverture se fera à 5m max de Sasuke.
    Izanami,izanagi et les chidori consorts sont prohibés

    Restriction NARUTO :
    — 5 clones nommés Alpha  
    — Création de 1000 clones autorisés pour un combo. Durent un tour. À usage unique.
    — 03 Invocations (Bêtes) maximum une créature morte ne revient plus. Pa et ma comptent pour 01.
    — La destruction des échoppes fait apparaître le crapaud 15 m minimum au dessus de la cible
    — Mode ermite disponible dès le début utilisable sur 3 tours puis attente de 2 tours avant nouvel utilisation.
    — Mode chakra de Kurama dès le début et permanent. 
    — RSM dure trois tours réutilisable après trois tours.
    — Tête de Kurama dure trois tours, réutilisable après trois tours.
    —  Kurama complet Cf susanoo parfait
    — Genjutsu sonore/Chant des crapauds sur 15 m nécessite deux tours de préparation.
    — Pas de clonage de Kurama, mode baryon off, Régénération, Voyage au mont off
    — Pas de clonage de Kurama, mode baryon off, Régénération
    """,
    """Contexte: sasuke vs naruto. 
    Naruto esquive l'attaque initiale de Sasuke en effectuant un saut et une course circulaire imprévisible tout en activant son KCM. Il invoque Gamahiro qui écrase Sasuke, et lance un shuriken de magma sur la position initiale de Sasuke après l'écrasement.
    Sasuke a raté son attaque surprise et se retrouve potentiellement exposé à l'écrasement de Gamahiro et à l'explosion du shuriken de magma. L'issue de ces attaques dépend de la capacité de Sasuke à réagir au prochain tour.
    """,
    """
        Action: † SASUKE †
        Alors que le portail été apparu Naruto s'était déjà obstiné à prendre la fuite mais grâce au lien Sasuke pouvait sentir le chakra de Naruto en déplacement alors lorsque Naruto entamait son premier saut pour aller en arrière Sasuke effectue un sunshine de manière courbé en évitant le portail et il apparaît directement à 18m de Naruto et au même moment enchaîne avec Ameno donc le déplacement ne prend que 1s, pour se retrouver à 3 mètre de Naruto avant que celui ci lancé ses attaque arrivé en face il fut électrocuté par le nagashi qui s'étendait à 10m de rayon puis Sasuke lança son katana dans la tête de Naruto...
    """
]


# print(ask_gemini(prompt = "incarne Jiraya de l'anime Naruto Shippuden et fait un pave de texte de moins de 250 mots  representant tes actions pour debuter un combat entre toi et Nagato, fait des actions base sur les competences de jiraya et en respectant les principes de Roleplay textuelle. "))
#print(ask_gemini(prompt = textpad_verdict_prompt))
# res = ask_gemini(prompt = [
#     "Where is Atlanta located ? give the answer in json, with latitude and longitude"
# ])
#import json
# print(res)
# res  = str(res).replace("```json", "").replace("```", "").strip()
# jsons_data = json.loads(res)
# print(jsons_data)

client, temp_file = authenticate_genai_with_service_account()
prompt = "generate three images of female character avatar ideas for an adventure roleplaying game in the naruto verse."
path = f"media/story/avatars/avatar-image-{random.randint(1000,99999)}.png"
def generate_image(prompt, file_name= f"generated-image.png", reference_img=None):
    response = client.models.generate_content(
        model="gemini-2.0-flash-preview-image-generation",
        contents=(
            prompt,
            Part.from_uri(
                file_uri=reference_img,
                mime_type='image/png' if reference_img else None
                #data = open(reference_img, 'rb').read() if reference_img else None
            )

        ),
        config=GenerateContentConfig(response_modalities=[Modality.TEXT, Modality.IMAGE]),
    )
    images = []
    for part in response.candidates[0].content.parts:
        if part.text:
            print(part.text)
        elif part.inline_data:
            image = Image.open(BytesIO((part.inline_data.data)))
            image.save(f"media/{file_name}")
            images.append(image)
            
    return images 

# images = generate_image("Change the hair color to blue", file_name="test-image.png", reference_img = "gs://rpv-story-avatars/alpha.png")
# print(images)
