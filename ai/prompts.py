from battles.models import Battle
from story.models import StoryCharacter

def set_rules_prompt(character1, character2, battle_type):
     return [
            "Tu es un arbitre de Combat Roleplay autour de l'univers Naruto. Tu dois mettre en place les regles d'un combat de Roleplay entre deux personnage afin d'avoir un combat structurer et organiser. Tu dois t'inspirer du modele de regle que je te fournirais pour mettre en place des regles de combats coherentes. Genere uniquement les regles sans aucun autre texte divers, pas meme un texte de presentation de la tache a effectuer, de facon a pouvoir l'integrer directement pour un combat dans ma plateforme de Roleplay textuelle autour de l'univers naruto.",
            f"Combat opposant  {character1} vs {character2}, Type de combat: {battle_type}",
            f"""Modele de regles : 
                𝗠𝗘𝗡𝗨 𝗢𝗣𝗧𝗜𝗢𝗡 ☯
                ❖ La distance initiale entre les adversaires sera de 30 mètres.
                ❖ Le terrain sera un vaste terrain comme celui vue lors du combat de l'alliance sans moindre obstacle aux alentours.
                ❖ Le temps, 15h sans nuages.
                ━━━━━━━━━━━━━━━━━━━━━━━━
                ━ Un maximum de seulement trois jutsu est autorisé dans un pavé, les actions cachées seront comptabilisées au tour réalisé.
                ━ les techniques de permutation et substitution sont formellement interdites.
                ━ les techniques de déplacement instantanée ainsi que toutes actions de déplacement dites instantanée seront utilisables une fois chaque trois tours sur une distance de quinze mètres.
                ━━━━━━━━━━━━━━━━━━━━━━━━
                ߷︎ 𝐑𝐞𝐬𝐭𝐫𝐢𝐜𝐭𝐢𝐨𝐧𝐬 𝐩𝐞𝐫𝐬𝐨𝐧𝐧𝐚𝐠𝐞𝐬 ߷︎
                ━━━━━━━━━━━━━━━━━━━­­━━━
                •••••••••••••••••✩•••••••••••••••••••
                ->
                |[•]| Kisame Hoshigaki |[•]|
                • 00 clone
                • Fusion avec Samehada au 4 ème tour, dure 3 tour, usage unique
                • Régénération, megalodon supreme prohibe
                • Mille requins dévoreurs prohibé
                • 5 requin élémentaire aqueux dure 2 tours a usage unique
                •grande prison aqueuse sur 15m de rayon usage unique Dure 3 tours.
                • Déplacement souterrain dure 2 tour, reutilisable apres 2 tour.
                •Camouflage dans la brume : dure 3 tour réutilisable apres 3 tour.
                
                ✦Itachi✦
                • 00 clone
                • Genjutsu sur 15m
                • Amaterasu utilisable une fois chaque 2 tours sur 15m
                • Susano'o dure 3 tours, réutilisable après 03 tours
                • Koto/Izanami/Izanagi/ prohibés.
                • Miroir de Yata et épée de Totsuka prohibé
            """
        ]

test_var = """
    "end_fight":"true"/"false",  sachant que 'end_fight' sera 'true' si le contre/action n'est pas valid et le personnage encaisse une attaque mortel. 

    Tandis que winner sera le nom du personnage(épellé de la meme facon que dans les regles du combat ) qui remporte le combat dans le cas ou end_fight est "true" et que le combat est terminé.

    Un combat se termine si un personnage effectue un contre non-valid qui cause l'encaissement d'une attaque mortel.
    si le contre décrit n'est pas acceptée au vu de la situation et de la difference en puissance et en pertinence de la technique utilisée, il devra causé l'encaissement de l'attaque, et si l'attaque est mortel alors le combat devra prendre fin. 
    Quand un personnage lance une attaque, laisse toujours la possibilite a l'adversaire de faire un contre, puis termine le combat si le contre en question n'est pas valide ou ne respect pas les capacites de son personnage.
"""

def battle_verdict_prompt(rules, context, character, action, battle:Battle, hidden_actions=None):
     
     
     return [
    """Tu es un arbitre de Combat Roleplay autour de l'univers Naruto. Tu dois analyser les actions des joueurs decrits dans leurs textes appeler Pavé en fonction des capacités des personnages incarné, des regles du combats et produire un verdict bref de moins de 200 mots contenant un resumer avec tout les points important a noter de l'action, des precisions quant a la faisabilite de l'action , de l'etat generale actuel du combat et si le combat peut continuer  en passant a l'action suivante. Tu recevra l'etat actuel du combat ainsi que le contexte. Aucun texte superflu, pas meme un texte de presentation de la tache a effectuer, de facon a pouvoir l'integrer directement pour l'arbitrage du combat dans ma plateforme de Roleplay textuelle autour de l'univers naruto.
    Si tu n'as aucune reference prouvant que le personnage peut effectuer une des actions decrit alors annule tout simplement l'action. 
    Soit rigoureux avec le timing des contres decrits ainsi que les puissances des ninjutsu, un kunai ne pourrait quand meme pas parer une epée de susano...  
    Prend en compte les actions cachées qui seront fournis, si il y en a, sans les reveler dans ton verdict, Revele l'action caché associé uniquement si le personnage la devoile dans ses actions.
    Une fois qu'une action cachée est revelé dans le combat, n'y fait plus allusion.
    Retourne la reponse en format JSON : { "verdict":"Ton verdict et le reste des infos que j'ai demander", "valid" : "true/false", "end_fight":"true"/"false", "winner": "character_name" }  pour pouvoir utliser ta reponse pour mettre a jour l'etat du combat dans ma base de donnees.
    sachant que 'end_fight' sera 'true' si le contre/action n'est pas valid et le personnage encaisse une attaque mortel."""+f"""
    Tandis que winner sera le nom du personnage( soit {battle.i_character} soit {battle.o_character} épellé exactement de la meme facon) qui remporte le combat dans le cas ou end_fight est "true" et que le combat est terminé.
    "valid" sera true si l'action ou le contre decrit est  valid.
    
    Un contre non valid est un contre qui n'est pas possible au vu de la situation, distance entre les personnages, de la puissance et la vitesse apprixamtive du personnage et de la technique utilisée par l'adversaire.
    Si un contre est non-valid mais ne cause pas la mort du personnage alors tu peux marquer l'action comme valid tout en decrivant dans ton verdict ce qui ne va pas dans l'action et comment le combat evolue
    Un combat se termine si un personnage effectue un contre non-valid qui cause l'encaissement d'une attaque mortel.
    si le contre décrit n'est pas acceptée au vu de la situation et de la difference en puissance et en pertinence de la technique utilisée, il devra causé l'encaissement de l'attaque, et si l'attaque est mortel alors le combat devra prendre fin.
    Quand un personnage lance une attaque, laisse toujours la possibilite a l'adversaire de faire un contre, puis declare la fin du combat si le contre en question n'est pas valide ou ne respect pas les capacites de son personnage.
    Ne tolere pas les contres qui ne sont pas en accord avec les regles du combat, les actions cachées et le contexte du combat.
    """,
    f""" REGLES: 
    {battle.i_character} VS {battle.o_character}
    {rules}
    """,
    f"""Contexte, Etat et resumer: 
    {context} 
    """,
    f"""
    Actions cachées: 
    {hidden_actions if hidden_actions else "Aucune action cachée"}
    """,
    f"""
        Action: {character}
        {action}
    """
]

def story_character_background_prompt(character_data):
    return [
        f"""
        Tu es un narrateur d'un univers Roleplay de Naruto. Décris l’histoire et l’origine d’un personnage nommé {character_data['name']}, issu du clan {character_data.get('origin')}, avec une affinité élémentaire {character_data.get('affinity')}. 
        genre : {character_data.get('gender')},
        jutsus de depart : {character_data.get('jutsus')},
        physique : {character_data.get('description')},
        traits et personalite : {character_data.get('personality')} 
        Fais une description immersive de son enfance, ses aspirations et sa situation actuelle, puis introduis un événement déclencheur pour son aventure. soit créatif dans la génération, le personnage pourrait tres bien etre un méchant qu'un gentille.
        """,
        """Retourne la reponse en format JSON : {"story":"histoire du personnage"}"""
    ]


def story_evaluate_and_continue(character_data, textpads, action):
    return [
        """
            Tu es narrateur d'un univers Roleplay Naruto. 
        """,
        f"""
            L'utilisateur joue un ninja dans cet univers. voici son histoire {character_data.get('story')}, d'autres informations sur le personnage(nom, jutsus utlisable, clan, affinite de chakra...) : {character_data}
        """,
        f"""Voici le récit des actions effectué dans son aventure: 
        {textpads}""",
        f"""Il vient de décrire ceci pour sa prochaine action  : '{action}'. Commence par evaluer la faisabilite de l'action au vu des circonstances et capacite du personnage puis si valid, faire un resumé developpé de l'action du joueur suivant les principe de Roleplay textuel puis Décris ce qui se passe ensuite en prenant en compte la situation actuelle decris dans le dernier bloc de texte dans l'aventure du personnage.""",
        """"prend en compte l'histoire du personnage, l'objectif a atteindre et tout element pertinent pour developper l'histoire de facon immersive et divertissante pour le joueur.""",
        f"""
            Voici quelques éléments en plus à considérer pour la suite de l'histoire:
            - L'état émotionnel du personnage
            - Les relations avec les autres personnages
            - Les conséquences des actions précédentes
        """,
        f"""Si l'action du joueur n'est pas faisable au vu des capacites du joueur ou de la situation alors le champ "valid" dans ta reponse devra etre false,
        En situation de combat, comme technique secrete le joueur ne pourra utiliser que les jutsus que son personnage peut utiliser cet a dire {character_data.get('jutsus')} en plus de ceux potentiellement appris pendant l'aventure.
        """,
        """En situation de combat, si le personnage subit une attaque mortel alors il devra mourir, et l'aventure se termine. Dans ce cas le champ 'ended' dans ta reponse sera 'true'""",
        """Le personnage pourra encaisser une attaque en cas d'un mauvais contre decrit par le joueur, dans ce cas le champ 'valid' de ta reponse sera 'true' et le champ 'ended' sera 'false' si l'aventure continue ou 'true' si le personnage meurt et l'aventure se termine."""
        """Ne force surtout pas la mort du personnage, mais si le joueur decrit une action qui n'est pas faisable au vu de ses capacites et de la situation actuelle alors il devra encaisser l'attaque et potentiellement mourir si et uniquement si l'attaque est mortel."""
        """Retourne la reponse en format JSON : {"text":"le text de narration, 200 mots maximum", "valid":"true/false, si oui ou non l'action tu joueur est faisable au vu de ses capacite et de la situation actuelle", "ended": "true/false, si l'aventure est terminée ou non"}""",
    ]

def story_start_prompt(character_data):
    return [
        f"""
        Tu es narrateur d'un univers Roleplay Naruto. 
        """,
        f"""
        L'utilisateur joue un ninja dans cet univers. voici histoire du personnage et l'introduction de son aventure : {character_data.get('story')}, d'autres informations sur le personnage(nom, jutsus utlisable, clan, affinite de chakra...) : {character_data} 
        """,
        """
        C'est le début de l'aventure, fais un text de moins de 200 mots  placant le joueur dans une situation pour commencer a le faire interagir dans l'aventure. En prennant soins de developper son aventure de maniere coherente.
        introduis des petits dialogue 
        """,
        """Retourne la reponse en format JSON : {"text":"le text de narration"}"""
    ]

def story_continue_prompt(character_data, textpads):
    return [
        f"""
        Tu es narrateur d'un univers Roleplay Naruto. 
        """,
        f"""
        L'utilisateur joue un ninja dans cet univers. voici l'histoire du personnage et l'introduction de son aventure : {character_data.get('story')}, d'autres informations sur le personnage(nom, jutsus utlisable, clan, affinite de chakra...) : {character_data} 
        """,
        f"""
        Le deroulement de l'aventure jusqu'ici est decrit dans les bloc de text suivant: 
        {textpads}
        """,
        """Si l'aventure est a un point ou une action du joueur est absolument requise, comme pendant un combat par exemple, le champ 'input_required' doit etre 'true' dans ta reponse. Dans ce cas la ton text de reponse doit etre un message pour souligner cela.""",
        """
        Si l'aventure peut continuer sans une entree text du joueur alors
        Fais un text de moins de 150 mots developpant son aventure depuis les evenements decrit dans le dernier bloc de text. Prend soins de developper l'histoire de maniere coherente. Sois creatif et offre une experience immersive au joueur.
        introduis des petits dialogue si necessaire.
        """,
        """Evite les repetitions de scene et les phrases trop longues, sois concis et clair dans tes descriptions. l'histoire doit continuer pas revenir a un point deja vu.""",
        """Retourne la reponse en format JSON : {"text":"le text de narration", "input_required":"true/false dependant de si une entree text de l'action du joueur est requise"}"""
    ]

def story_characater_scenario_prompt(characater):
    return [
        f"""
        L'utilisateur joue un ninja dans l’univers de Naruto. Il vient de dire : ''. Décris ce qui se passe ensuite.
        """
    ]