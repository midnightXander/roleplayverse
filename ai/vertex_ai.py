from google import genai
from google.genai.types import HttpOptions
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.environ.get('GEMINI_API_KEY') 

#client =  genai.Client(http_options= HttpOptions(api_version='v1'), api_key=api_key)
# response = client.models.generate_content(
#     model = "gemini-2.0-flash-001",
#     contents = "Quels sont les points forts de Naruto dans l'anime naruto shippuden ",
# )



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