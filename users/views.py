from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.models import User,auth
from django.urls import reverse
from django.http import HttpResponseRedirect,JsonResponse,Http404
from django.contrib.auth import logout,login,authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *
from core.models import Post,Notification,SavedPost
from battles.models import BattleAcceptor,BattleRequest,Battle,RefreeingProposal,battle_status,Challenge

import battles.views as battle_views
import uuid
from django.db.models import Q,QuerySet
import re
from dateutil.relativedelta import relativedelta
import datetime
import core.views as core_views
from utility import _time_since,sendWelcomeEmail,sendResetPasswordLink
from .users_utility import *
from django.core.serializers import serialize
from django.forms.models import model_to_dict
from django.views.decorators.csrf import csrf_exempt

import string,random,secrets


def test_template(request):
    return render(request, "users/test_template.html")

 

def contains_special_chars(text):
    # Define the regex pattern for special characters
    pattern = re.compile(r'[!@#$%^&*(),.?":{}|<>-]')

    # Search for the pattern in the input string
    if pattern.search(text):
        return True
    else:
        return False


def validate_info(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if(password1 == password2):
            # user = User.objects.create_user(username=username,email=email,password=password1)
            user = username
            return HttpResponseRedirect(reverse("users:register",args=[user]))   

        else:
            messages.error(request,"Invalid infos")    
            return HttpResponseRedirect(reverse("users:validate")) 

    return render(request,"users/validate_info.html")

def getusernames(users):
    usernames = []
    for user in users:
        username = user.username.lower()
        usernames.append(username)
    return usernames

def get_family_names(families):
    names = []
    for family in families:
        name = family.name.lower()
        names.append(name)
    return names

def get_emails(users):
    emails = []
    for user in users:
        email = user.email
        emails.append(email)
    return emails


def verify_username(request):
    if request.method == "POST":
        all_users = User.objects.all()
        usernames = getusernames(all_users)
        username = request.POST["username"]
        username = username.lower()
        message = ""
        status = "invalid"
        if len(username) < 5:
            message = "Nom d'utilisateur trop court" 
            return JsonResponse({"status":status, "message":message})  
        elif " " in username:
            message = "le nom d'utlisateur ne doit pas contenir d'espace"
            return JsonResponse({"status":status, "message":message})
        elif "/" in username or '\\' in username:
            message = "le nom d'utlisateur ne doit pas contenir de caractère spécial"
            return JsonResponse({"status":status, "message":message})  
        elif contains_special_chars(username):
            message = "le nom d'utlisateur ne doit pas contenir de caractère spécial"
            return JsonResponse({"status":status, "message":message}) 
        elif username in usernames :
            message = "ce nom d'utlisateur est deja pris, choisi en un autre "
            return JsonResponse({"status":status, "message":message}) 
        
        #Should not start with a number

        else:
            status = "valid"
            message = "Valid username"

        return JsonResponse({"status":status, "message":message})    



def verify_email(request):
    if request.method == "POST":
        all_users = User.objects.all()
        emails = get_emails(all_users)
        email = request.POST["email"]
        message = ""
        status = "invalid"
        if "@" not in email:
            message = "L'email doit contenir @" 
            return JsonResponse({"status":status, "message":message})  
        elif " " in email:
            message = "l'email ne doit pas contenir d'espace"
            return JsonResponse({"status":status, "message":message}) 
        elif email in emails :
            message = "l'email a déja été utlisé"
            return JsonResponse({"status":status, "message":message}) 
        else:
            status = "valid"
            message = "email valid"

        return JsonResponse({"status":status, "message":message})    

def verify_password(request):
    if request.method == "POST":
        status = "invalid"

        password = request.POST["password"]
        
        if len(password)<8:
            message = "mot de passe trop court, minimum 8 caractére"
            return JsonResponse({"status":status, "message":message})
        else:
            status = "valid"
            message = "Le mot de passe est valid"
            return JsonResponse({"status":status, "message":message})

def verify_passwords(request):
    if request.method == "POST":
        status = "invalid"
        message = "Les mots de passes ne sont pas identiques"

        password1 = request.POST["password1"]
        password2 = request.POST['password2']

        if password1 == password2:
            status = "valid"
            message = "Les mot de passes correspondent"
            return JsonResponse({"status":status, "message":message})
        else:
            return JsonResponse({"status":status, "message":message})


def verify_family_name(request):
    if request.method == "POST":
        all_families = Family.objects.all()
        names = get_family_names(all_families)
        name = request.POST["name"]
        name = name.lower()
        message = ""
        status = "invalid"
        if len(name) < 5:
            message = "Nom trop court" 
            return JsonResponse({"status":status, "message":message})  
        elif " " in name or contains_special_chars(name): #test if name contains spaces or special characters
            message = "Le nom de famille ne doit pas contenir d'espace ou de caractère spéciaux"
            return JsonResponse({"status":status, "message":message}) 
        elif name in names:
            message = "une famille avec ce nom existe déja"
            return JsonResponse({"status":status, "message":message}) 
        elif len(name) > 25:
            message = "Nom de famille trop long, moins de 25 caractères autorisés"
            return JsonResponse({"status":status, "message":message}) 
        
        #Should not start with a number

        else:
            status = "valid"
            message = "nom valid"

        return JsonResponse({"status":status, "message":message})    

def generate_reset_key():
    """Function to generate a key that is used to  let users reset their passwords for a certain time"""
    key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    return key

def password_recover(request):
    if request.method == "POST":
        user_data = request.POST['user_data']
        
        user = User.objects.filter(Q(username = user_data) | Q(email = user_data)) 
        if len(user)>0:
            
            #send email with link
            user = user[0]
            user_email = user.email
            try:
                player = Player.objects.get(user = user)
                code = PasswordRecoveryCode.objects.create(key = generate_reset_key(), player = player)
                link = f"https://roleplayverse.com/users/password/reset?k={code.key}"
                print(f"sent {link} to {user_email}")
                
                code.save()
                
                #sendResetPasswordLink(user_email)                
                messages.success(request, f"Un lien a été  envoyé a {user_email}")
            except Exception as e:
                print(f"Error in sending link to {user_email}: {e}") 
                messages.error(request, "Une erreur s'est produite pendant l'envoie du mail")   
        else:
            messages.error(request, "Aucun utlisateur n'a été trouvé avec ce nom d'utlisateur ou email")

    return render(request, "users/accounts/password_recover.html")

def password_reset(request):
    
    key = request.GET.get('k')
    
    code = get_object_or_404(PasswordRecoveryCode,key = key)
    
    #get the difference in days since created and delete if greater than or equal to 1
    now = timezone.now()
    difference = now - code.date_created

    days = difference.days
    if days >=1:
        code.delete()
        raise Http404
        # validity = {
        #     'value': False,
        #     'message':"ce lien n'est plus valid"
        # }
    if key:
        player = code.player
        user = player.user
        if request.method == 'POST':
            new_password = request.POST['new_password']
            new_password2 = request.POST['new_password2']

            if new_password == new_password2:
                if len(new_password) < 8:
                    messages.error(request, 'Le mot de passe doit contenir au moins 8 charactere')
                    return redirect(f'/users/password/reset?k={key}')
                
                else:    
                    user.set_password(new_password)
                    user.save()
                    messages.success(request, "Votre Mot de passe a été changé avec succès")
                    code.delete()

                    return redirect('/users/signin')
            else:
                messages.error(request, 'Les mot de passe ne sont pas identiques')
                return redirect(f'/users/password/reset?k={key}')


        return render(request, "users/accounts/password_reset.html",{
            "validity":True,
            'key': key,
            
        })
    else:
        print("No key")
        raise Http404

def _name_suggestion():
    return 'WerenLyrics'

def register(request):
    
    
    if request.method == "POST":
        username:str = request.POST["username"]
        username = username.strip()
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
            

        if(password1 == password2):
            if User.objects.filter(email=email).exists():
                messages.info(request,"l'email est deja utilisé")
                return HttpResponseRedirect(reverse("users:register"))
            elif User.objects.filter(username=username).exists():
                messages.error(request,"le nom d'utilisateur est deja utilisé")
                return HttpResponseRedirect(reverse("users:register"))
            else:        
                new_user = User.objects.create_user(username=username,email=email,password=password1)
                # new_player = Player.objects.create(
                #     user = new_user,
                #     language = request.LANGUAGE_CODE,
                #     country = get_country(request)
                #     )
                # new_stats = PlayerStat.objects.create(player = new_player)
                user_auth = auth.authenticate(username = username,password=password1)
                auth.login(request,user_auth)
                
                #Award entry battle points
                
                new_player = Player.objects.get(user = new_user)
                new_player.language = request.LANGUAGE_CODE
                new_player.country = get_country(request)
                print(get_country(request))
                profile_pics = PlayerDefaultImage.objects.all()
                new_player.profile_picture = profile_pics[random.randint(0,len(profile_pics)-1)].image
                
                new_player.save()

                core_views.add_points(new_player, ENTRY_POINTS)

                new_user.save()
                new_player.save()
                # new_stats.save()

                try:
                    sendWelcomeEmail(new_user.email)
                except Exception as e:
                    print(f"could not send email: {e}")    

                # new_notif = core_views.Notification.objects.create(
                #     target = new_player,
                #     url = '#',
                #     content = f'Bienvenue sur RolePlay Verse {new_player} pourquoi pas commencé un combat amicale pour voir comment ça se passe ici?'
                # )
                # new_notif.save()

                #Reward the referer if there is one
                referall_code = request.GET.get('rc', None)
                if referall_code:
                    refer_player(referall_code)

                return HttpResponseRedirect(reverse("users:player",args=[new_user.username]))   

        else:
            messages.error(request,"Les mots de passes ne correspondent pas")    
            return HttpResponseRedirect(reverse("users:register")) 

    return render(request,"users/register.html",{
        "characters":ch_names,
        'name_suggestion': _name_suggestion(),
        })


def login(request):
    player = get_player(request.user)
    if player:
        return redirect('/home')
    
    if request.method == "POST":
        user_data = request.POST["email"]
        password = request.POST["password"]
        user = User.objects.filter(Q(username = user_data) | Q(email = user_data))

        try:    
            # user = User.objects.get(email=user_data)
            user = user[0]
        except:
            messages.error(request,"Aucun n'utilisateur avec cet email ou nom d'utilisateur")
            return HttpResponseRedirect(reverse("users:login")) 
        
        user_auth = auth.authenticate(username=user.username,password=password)
        if user_auth is not None:
            auth.login(request,user_auth)
            return HttpResponseRedirect(reverse("core:home"))
        else:
            messages.error(request,"Mot de passe incorrect")
            return HttpResponseRedirect(reverse("users:login"))


    return render(request,"users/login.html")

def logout_view(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse("users:login"))

@login_required
def family(request):
    try:
        family = Family.objects.get(god_father=request.user)
    except:
        messages.info(request,"You have no family") 
        return HttpResponseRedirect(reverse("users:new_family"))
        
    members = Player.objects.filter(family=family)
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)
    context = {"family":family, "members":members, "player":player,"n_notifs":n_notifs}
    return render(request,"users/family/family.html",context)

@login_required
def new_family(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    own_family = Family.objects.filter(god_father = player.user).exists()
    if request.method == "POST":
        name = request.POST["familyName"]
        description = request.POST.get("family-bio")
        profile_pic = request.FILES.get("family-picture")
        #all_families = list(Family.objects.all())
        if player.family:
            messages.error(request,"Tu es deja dans une famille, quitte ta famille actuel pour en créer une")
            return HttpResponseRedirect(reverse("users:new_family"))

        elif Family.objects.filter(name=name).exists():
            messages.error(request,"Une famille avec ce nom existe deja")
            return HttpResponseRedirect(reverse("users:new_family"))
        elif not profile_pic:
            messages.error(request,"Tu dois ajouter une photo de profile")
            return HttpResponseRedirect(reverse("users:new_family"))
        else:
            new_position = len(Family.objects.all()) + 1
            new_family = Family.objects.create(
                name=name,
                god_father = request.user,
                position = new_position,
                description = description,
                )
            if profile_pic:
                new_family.profile_picture = profile_pic
                
            #user = User.objects.get(username=request.user.username)
            player = Player.objects.get(user=request.user)
            player.family = new_family   

            #ADD The GodFather badge to the player
            godfather_badge = Badge.objects.get(title = "GodFather")
            player.badges.add(godfather_badge)

            new_family.save()
            player.save()
            messages.success(request,"Famille Crée avec succès")
            new_notif = Notification.objects.create(
                target = player,
                content = "Felicitation, tu es desormais un parrain de famille! et si tu commencais a recruter quelques membres ?",
                url = f"/users/family/{new_family.id}",
            )

            new_notif.save()
            #return redirect(f'/users/family/65744{new_family.id}')
            return HttpResponseRedirect(reverse("users:family_page", args=[new_family.id]))

    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)

    return render(request,"users/family/new_family.html",
                  {"player":player,
                   "own_family":own_family,
                   "n_notifs":n_notifs})

def send_invite(request,target_id):
    if request.method == "POST":
        sender = Player.objects.get(user = request.user)
        target = get_object_or_404(Player,id = target_id)
        family = sender.family
        message = 'bad request'
        if sender.user != family.god_father:
            message = "Tu ne peux inviter des joueurs a rejoindre ta famille"

        elif PlayerNotification.objects.filter(notif_type ='invite',sender = sender, target = target).exists():
            message = "Tu as deja envoyé une invitation non répondu a ce joueur"
        
        else:
            message = "Invitation envoyé"
            new_player_notification = PlayerNotification.objects.create(
                notif_type = "invite",
                sender = sender,
                target = target,
                family = sender.family
                )
            new_player_notification.save()
            print(f'invite sent to {target}')
            return JsonResponse({"status":"success","message": message})
    return JsonResponse({'status':'failed', "message":message})

def send_request(request,family_id):
    if request.method == "POST":
        family = Family.objects.get(id=family_id)
        sender = Player.objects.get(user = request.user)
        
        god_father = family.god_father
        target = get_object_or_404(Player, user = god_father)

        message = ''
        if sender.family:
            message = f"Tu es deja dans une famille, tu dois quitté  {sender.family} pour essayer de rejoindre une autre famille"
        elif PlayerNotification.objects.filter(notif_type ='request',sender = sender, family = family).exists():
            #check if player already has a request to join that family
            message = 'Tu as déja une requete en attente pour rejoindre cette famille'

        else:    
            message = f'requète envoyé pour  {family.name}'
            new_player_notification = PlayerNotification.objects.create(
                notif_type = "request",
                sender = sender,
                target = target,
                family = family,
                )
            new_player_notification.save()
            return JsonResponse({"status":"success", 'message': message})
    return JsonResponse({"status":"failure",'message':message})

def join_family(request,notif_id):
    if request.method == "POST":
        player = Player.objects.get(user=request.user)
        notif = get_object_or_404(PlayerNotification, id = notif_id)
        family = notif.family
        
        if player.family:
            message = 'tu es deja dans une famille'
        else:
            player.family = family
            #new_name = player.user.username + " " + family.name
            family.save()
            player.save()
            notif.delete()
            
            return JsonResponse({'status' : 'success', "message" : f"successfully joined {family}"})
    
    return JsonResponse({"status" : "failed", 'message' : message})    


def accept_request(request,notif_id):
    if request.method == "POST":
        player = get_object_or_404(Player, user = request.user)
        notif = PlayerNotification.objects.get(id = notif_id)
        family = Family.objects.get(god_father = request.user) 
        player_to_add = notif.sender
        
        #get the player notification concerned
        #delete it after adding the player
        if player_to_add.family:
            message = "Le joueur a deja integré une autre famille"
        elif player.user != family.god_father:
            message = 'Seul le parrain de la famille peut ajouter des nouveaux membres'    
        else:
            player_to_add.family = family
            #new_name = player_to_add.user.username + "("+family.name+")"
            #player_to_add.user.username += f"({family.name})"
            # player_to_add.user.username = new_name
            notif.delete()
            family.save()
            player_to_add.save()
            message = "Le joueur a été ajouté a la famille"

            return JsonResponse({'status':'success', 'message':message})
            
        return JsonResponse({'status':'failed', 'message':message})

def refuse_request(request,notif_id):
    if request.method == "POST":
        notif = PlayerNotification.objects.get(id = notif_id)
        new_notif = PlayerNotification.objects.create(
            notif_type = "refused_request",
            sender = notif.target,
            target = notif.sender,
            family = notif.family
        )
        new_notif.save()
        notif.delete()
        
        return JsonResponse({"status":"success", "message":"Request refused"})
    return JsonResponse({"status":"failure", "message":"Request not refused"})            

def _can_add_members(player:Player,family:Family):
    family = family
    if not family:
        return False
    elif family.god_father == player.user:
        #Make it based on role
        return True
    else:
        return False



@login_required    
def family_page(request,family_id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    family = Family.objects.get(id = family_id)
    members = Player.objects.filter(family=family)
    battles = Battle.objects.filter(
        Q(status = battle_status[1]) | Q(status = battle_status[2]) | Q(status = battle_status[3])
        ).order_by('-date_started')
    family_battles = []
    for member in members:
        for battle in battles:
            if member == battle.initiator or member == battle.opponent:
                family_battles.append(battle_views._battle_data(member, battle))
    
    #get family roles  
    roles = []
    # recruiter_badge =  Badge.objects.get(title = 'Recruiter')
    # roles.append(recruiter_badge)            
    
    context = {
        "family":family,
        "members":members,
        'ranking':get_ranking(family.name),
        "n_members": len(members),
        "player":player,
        "battles": family_battles,
        "recent_battles": family_battles[:3],
        "roles":roles,
        'can_add': _can_add_members(player,family),
        "n_notifs":core_views.get_notifs(player),

        }
    return render(request,"users/family/family_page.html",context)


def family_battles(request,family_id):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    family = Family.objects.get(id = family_id)
    members = Player.objects.filter(family=family)
    battles = Battle.objects.filter(
        Q(status = battle_status[1]) | Q(status = battle_status[2]) | Q(status = battle_status[3])
        ).order_by('-date_started')
    
    family_battles = []

    def battle_in_family(battle):
        for family_battle in family_battles:
            if battle.id == family_battle['id']:
                return True
        return False    

    for member in members:
        for battle in battles:
            if member == battle.initiator or member == battle.opponent:
                #check if the battle is already in the list of family battles
                if not battle_in_family(battle):
                    family_battles.append(battle_views._battle_data(member, battle))
    
    if request.method == "POST":
        
        #battles_data = battle_views._battles_data(player, family_battles)
        return JsonResponse({
        "battles": family_battles,
        "status": "success",
        })
    
    return render(request, "users/family/battles.html",{
        "family":family,
        'ranking':get_ranking(family.name),
        "n_members": len(members),
        "player":player,
        "battles": family_battles,
        "recent_battles": family_battles[:3],
        "n_notifs":core_views.get_notifs(player),

    })

def get_acceptors(req: BattleRequest):
        accepted_requests_list = []
        accepted_requests = BattleAcceptor.objects.filter(request = req)
        # for a_request in BattleAcceptor.objects.all(): 
        #     if a_request.request.sender == req.sender:     
        #         accepted_requests.append(a_request)

        #IMPLEMENT can_accept function for buttons on the frontend
        return accepted_requests

def get_refree_propsals(battle_request, player):
    #battle = Battle.objects.get(request = battle_request)
    proposals = []
    for proposal in RefreeingProposal.objects.all():
        if proposal.battle:
            if proposal.battle.request == battle_request:
                proposals.append(proposal)
    return proposals

def _can_invite(player1:Player, player2:Player):
    family = player1.family
    if family:
        god_father = family.god_father
    else:
        god_father = None    
    
    can_invite = True
    
    #CHANGE this to be based on roles
    if player1.family ==  player2.family:
        can_invite = False
    elif player1.user != god_father:
        can_invite = False

    return can_invite  

# def _can_add_members(player:Player):
#     family = player.family
#     if family:
#         god_father = family.god_father
#     else:
#         god_father = None    
    
#     can_add = False
    
    #CHANGE this to be based on roles
    # if player.user == god_father:
    #     can_add = True

    # return can_add 
       


def _player_data(player:Player):
    return{
        'id': player.id,
        'name': str(player),
        'user':{
            'id': player.user.id,
            'username':player.user.username,
            'email':player.user.email,
        },
        'profile_picture': player.profile_picture.url,
        'rank': player.rank,
        'progression': player.progression,
        'ranking' : 10,
        'nickname' : player.nickname,
        'wins': _total_wins(player)
        

    }

def _sent_invite(sender, target):
    return PlayerNotification.objects.filter(notif_type ='invite',sender = sender, target = target ).exists()

def get_players(request):
    if request.method == 'POST':
        filter = request.POST.get('filter')
        current_player = get_object_or_404(Player,user = request.user)
        if filter  == 'invite-family':
            family_id = request.POST.get('family_id')
            family = Family.objects.get(id = family_id)
            #family = current_player.family
            players = Player.objects.exclude(family = family).order_by('-progression')
            
            
            players_data = [ _player_data(player)  for player in players if not _sent_invite(current_player,player)]

            return JsonResponse({'players': players_data, 'status':'success'})

    return JsonResponse({'status':'failed'})    
            




@login_required
def player(request,name):
    
    user = get_object_or_404(User, username = name)
    player = Player.objects.get(user = user)

    c_player = get_player(request.user)
    if not c_player:
        return redirect('/users/signin')
    
    player_requests = BattleRequest.objects.filter(sender = player)    
    can_edit = False
    if player == c_player:
        can_edit = True
    player_requests = [
        {
            "id":request.id,
            "type":request.type,
            "sender": request.sender,
            "character": request.character,
            "acceptors": get_acceptors(req=request),
            "refree_proposals": get_refree_propsals(player=player, battle_request=request)
        } 
        for request in player_requests
    ]
    badges = player.badges.all()
    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player)
    }
    posts = Post.objects.filter(author = player).order_by('-date_added')

    player_notifs = PlayerNotification.objects.filter(target= c_player, read = False)
    n_notifs = len(player_notifs)


    if request.method == "POST":
        posts_data = core_views._posts_data(player,posts)

        return JsonResponse({'posts':posts_data, "status":"success"})


    context = {"req_player":player,
               "player":c_player,
               "requests":player_requests,
               "n_notifs":core_views.get_notifs(c_player),
               "posts":posts, 
               "stats":stats,
               "badges": badges,
               "can_edit":can_edit,
               'can_invite': _can_invite(c_player, player),
               "characters":ch_names,
               
               }
    return render(request,"users/user/user_page.html",context)

@login_required
def player_profile(req):
    player = Player.objects.get(user = req.user)
    player_requests = BattleRequest.objects.filter(sender = player) 
    #stats = PlayerStat.objects.get(player = player)
    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player)
    }
    
    player_requests = [
        {
            "id":request.id,
            "type":request.type,
            "sender": request.sender,
            "character": request.character,
            "acceptors": get_acceptors(req=request),
            "refree_proposals": get_refree_propsals(player=player, battle_request=request)
        } 
        for request in player_requests
    ]
    posts = Post.objects.filter(author = player)
    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)
    
    context = {"player":player,
               "requests":player_requests, 
               "posts":posts, 
               "stats":stats,
               "n_notifs":core_views.get_notifs(player) }
    return render(req,"users/user/profile.html",context)



def edit_info(request):
    player = Player.objects.get(user = request.user)
    if request.method == "POST":
        info = request.POST.get("info")
        if info == "bio":
            player.bio = request.POST.get("bio")
        elif info == "nickname":
            player.nickname = request.POST.get("nickname")  
        elif info == "profile-picture":
            profile_pic = request.FILES.get("profile-picture")
            
            if profile_pic:
                player.profile_picture = profile_pic
            else:
                player.profile_picture = '/blank-profile-picture.png'
        elif info == "username":
            """Add some verification here"""
            #1 - unique username
            #2 - sufficient number of characters
            #3 - No special characters
            new_name = request.POST.get('username')
            users = User.objects.filter(username = new_name)
            if users.exists():
                messages.error(request, 'un utilisateur avec ce nom existe déja')
            
            else:
                player.user.username = new_name

                player.user.save()
        player.save()    

        #return JsonResponse({"status":"success","message":"modified","info":info})
        return HttpResponseRedirect(reverse("users:player", args=[player.user.username]))
    return JsonResponse({"status":"error","message":"nothing modified"})



def get_family_players(family):
    players = Player.objects.filter(family = family)
    return players

def get_eligibility(player,family):
    """returns true if player has a request to join that 
family hence making the non eligibility test in the frontend run true and disable 
the request btn"""
    eligibility =  PlayerNotification.objects.filter( 
       Q(notif_type = "request") & Q(sender = player) & Q(family = family )
        ).exists()
    return  eligibility   
    
def remove_member(request,player_id):
    if request.method == "POST":
        player = Player.objects.get(user = request.user)
        player_to_remove = Player.objects.get(id = player_id)
        #ensure current player can remove members
        #check if player has a stake or tournament battle ongoing
        ongoing_battles = Battle.objects.filter(
            # (Q(status = battle_status[0]) | Q(status = battle_status[1]) | Q(status = battle_status[2])),
            Q(initiator = player_to_remove) | Q(opponent = player_to_remove)           
        ).exclude(status = battle_status[3])
        

        if player.user != player.family.god_father :
            message = "tu n'es pas authorizé a retiré des membres"
        elif player == player_to_remove:
            message = "tu ne peux pas te retiré toi meme"
        elif ongoing_battles.exists():
            message = "Le joueur a un combat stake/tournoi en cours, le combat doit étre terminé avant de pouvoir retiré d'autres joueurs" 
        else:
            #promotion logic
            return JsonResponse({'status':'success','message':f'{player_to_remove.user} removed from {player.family}'})     
    return JsonResponse({'status':'failure','message':message})
        

def promote_member(request,player_id):
    #ensure current player can promote members
    #get the badge and ensure player does not have that badge already
    if request.method == "POST":
        role = request.POST['role']
        badge =  Badge.objects.get(title = role)
        player_to_promote = Player.objects.get(id = player_id)
        player = Player.objects.get(user =  request.user)

        if player.user != player.family.god_father :
            message = "Tu n'es pas authorizé a promouvoir des joueurs"
        elif player == player_to_promote:
            message = "Tu ne peux pas te promouvoir toi meme"
        elif badge in player_to_promote.badges.all():
            message = 'Le joueur a deja ce role'  
        else:
            #promotion logic
            return JsonResponse({'status':'success','message':f'{player_to_promote.user} promoted to {badge} role'})     
    return JsonResponse({'status':'failure','message':message})

     

def demote_member(request, player_id):
    #ensure current player can demote members
    #get the badge and ensure player has that badge already
    if request.method == "POST":
        role = request.POST['role']
        badge =  Badge.objects.get(title = role)
        player_to_demote = Player.objects.get(id = player_id)
        player = Player.objects.get(user =  request.user)

        if player.user != player.family.god_father :
            message = "You are not authorized to demote players"
        elif player == player_to_demote:
            message = "You can't demote yourself"
        elif badge not in player_to_demote.badges.all():
            message = 'The player does not  have that role'  
        else:
            #promotion logic
            return JsonResponse({'status':'success','message':f'{player_to_demote.user} demoted from {badge} role'})     
    return JsonResponse({'status':'failure','message':message})

@login_required
def families(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    eligible = True

    if player.family:
        eligible = False 
    families = Family.objects.all().order_by('-date_created')
    families_data = [
        {
            "family":family,
            "n_members": len(get_family_players(family)),
            "eligible_to_request":  get_eligibility(player,family),
            'rank': get_ranking(family.name),
        } for family in families
    ]

    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)
    context = {"families":families_data, "player":player, 
               "eligible":eligible,
               "n_notifs":n_notifs}
    return render(request,"users/family/families.html",context)

@csrf_exempt
def player_notif(request,id,type):
    if request.method == "DELETE":
        if type == 'generic':
            notification = Notification.objects.get(id = id)
            notification.delete()
            return JsonResponse({'status':'success', 'message':'Deleted'})
        elif type == 'game':
            notif = PlayerNotification.objects.get(id = id)
            notif.delete()
            return JsonResponse({"status":"success","message":"Deleted"})
    return JsonResponse({"status":"failure","message":"error pperforming operation"})


def get_player_battles(request,name):
    #get the player objects or raise a 404  
    user = get_object_or_404(User,username = name)
    c_player =get_object_or_404(Player,user = request.user)
    player = get_object_or_404(Player,user = user)

    battles = Battle.objects.filter(
        Q(initiator = player) | Q(opponent=player))
    
    ref_battles = Battle.objects.filter(
        Q(refree = player),
        #Q(status = battle_status[1] or battle_status[2]), #get battles either not_started or ongoing that the player is refreeing

                                         )
    
    combined_battles = battles.union(ref_battles) #combine the two querysets of battles
    combined_battles = combined_battles.order_by('-date_started') #sort by date


    battles_data = battle_views._battles_data(player, combined_battles)
    
        
    return JsonResponse({
        "battles": battles_data,
        "status": "success",
        })

@login_required
def player_battles(request,name):
    #get the player objects or raise a 404  
    user = get_object_or_404(User,username = name)
    c_player =  get_player(request.user)
    if not c_player:
        return redirect('/users/signin')
    
    player = get_object_or_404(Player,user = user)

    battles = Battle.objects.filter(
        Q(initiator = player) | Q(opponent=player))
    
    ref_battles = Battle.objects.filter(
        Q(refree = player),
        #Q(status = battle_status[1] or battle_status[2]), #get battles either not_started or ongoing that the player is refreeing

                                         )
    
    combined_battles = battles.union(ref_battles) #combine the two querysets of battles
    combined_battles = combined_battles.order_by('-date_started') #sort by date

    #stats = PlayerStat.objects.get(player = player)

    battles_data = battle_views._battles_data(player, combined_battles)
    if request.method == "POST":
        
        return JsonResponse({
        "battles": battles_data,
        "status": "success",
        })
    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player),
        "draws": 0
    }
    context = {"req_player":player,
               "can_edit":player == c_player,
               "stats":stats,
               "player":c_player, 
               "battles":battles_data,
               "stats":stats,
                "ref_battles":ref_battles,
                 'n_notifs':core_views.get_notifs(player),
                   }
    
    
    return render(request, "users/user/battles.html", context)

@login_required
def battle_requests(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    player_requests = BattleRequest.objects.filter(sender = player).order_by('-date_sent')    

    player_requests = [
        {
            "id":request.id,
            "type":request.type,
            "sender": request.sender,
            "character": request.character,
            "acceptors": get_acceptors(req=request),
            "refree_proposals": get_refree_propsals(player=player, battle_request=request),
            
        } 
        for request in player_requests
    ]
    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player),
        "draws": 0
    }
    player_notifs = PlayerNotification.objects.filter(target= player, read = False)
    n_notifs = len(player_notifs)
    context = {"player":player,
               "stats":stats,
               "requests":player_requests,
               "n_notifs":n_notifs}
    return render(request,"users/user/requests.html",context)

@login_required
def player_battle_requests(request,name):
    user = get_object_or_404(User,username = name)
    c_player = get_player(request.user)
    if not c_player:
        return redirect('/users/signin')
    player = get_object_or_404(Player,user = user)
    if c_player != player:
        raise Http404

    player_requests = BattleRequest.objects.filter(sender = player).order_by('-date_sent')      

    player_requests = [
        {
            "id":request.id,
            "type":request.type,
            "sender": request.sender,
            "character": request.character,
            "date_sent" : _time_since(request.date_sent),
            "expiry_date": request.expiry_date,
            "acceptors": get_acceptors(req=request),
            "refree_proposals": get_refree_propsals(player=player, battle_request=request),
            
        } 
        for request in player_requests
    ]
    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player),
        "draws": 0
    }
    
    #stats = PlayerStat.objects.get(player = player)

    context = {
        "req_player":player,
        "player":c_player,
        "stats":stats,
        "can_edit":player == c_player,
        "requests":player_requests,
        "n_notifs":core_views.get_notifs(c_player),
        }
    return render(request,"users/user/requests.html",context)


def player_posts(request,name):
    user = User.objects.get(username = name)
    player = Player.objects.get(user = user )
    posts = Post.objects.filter(author = player).order_by('-date_added')

    posts_data = [ {
            "feed_item": "post",
            "id": post.id,
            "author":{  
                        'id':post.author.id,
                        "name":post.author.user.username,
                        'player': str(post.author),
                        'profile_picture':post.author.profile_picture.url
                        },
            'body':post.body,
            'liked': core_views._liked_post(player, post),
            'likes':core_views._parse_number(post.likes),
            'image':post.image.url if post.image else None,
            "comments": core_views.get_comments_dict(post),
            "n_comments": len(core_views.get_comments(post)),
            "time_posted": _time_since(post.date_added),
        } for post in posts
        ]
    
    data = serialize('json',posts)
    return JsonResponse({'data':posts_data}, safe=False)

def _total_battles(player:Player,status=None):
    battles =  Battle.objects.filter(
        Q(initiator = player) | Q(opponent = player)
    ) 
    if status:
        battles = battles.filter(status = status)
    return len(battles)

def _total_wins(player:Player):
    battles =  Battle.objects.filter(
        winner = player
    )
    return len(battles)

def _total_losses(player:Player):
    total_battles = _total_battles(player,'finished')
    total_wins = _total_wins(player)
    return total_battles - total_wins

def _win_rate(player):
    total_battles = _total_battles(player)
    total_wins = _total_wins(player)
    if total_battles == 0:
        return 0
    win_rate = (total_wins/total_battles)*100
    return round(win_rate,1)

def _progress_per_month(player:Player):
    pass

def _most_used_character(player:Player):
    pass

def _battles_per_month(player:Player):
    pass

def _progress_per_month(player:Player):
    pass

def _favorite_character(player:Player):
    characters = []
    favorite_character = 'Aucun'
    battles = Battle.objects.filter(
         initiator = player 
    )
    for battle in Battle.objects.filter(initiator = player ):
        #get the characters of battles where player was initiator 
        characters.append(battle.i_character)
    for battle in Battle.objects.filter(opponent = player ):
        #get the characters of battles where player was opponent 
        characters.append(battle.o_character)

    character_count = {}
    for character in characters:
        if not character in character_count:
            #set the number of occurences of each character in the list
            character_count[character] =  characters.count(character)

    biggest_count = 0
    #get the character with the highest ocurrence
    for character, count in character_count.items():
        if count > biggest_count: 
            biggest_count = count
            favorite_character = character

    return favorite_character
  

    


@login_required
def stats(request, name):
    user = get_object_or_404(User,username = name)
    c_player = get_player(request.user)
    if not c_player:
        return redirect('/users/signin')
    player = get_object_or_404(Player,user = user)
    total_battles  =_total_battles(player)
    total_wins = _total_wins(player)
    total_losses = _total_losses(player)
    win_rate = _win_rate(player)
    favorite_character = _favorite_character(player)  

    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player),
        "draws": 0
    }
    
    #stats = PlayerStat.objects.get(player = player)

    context = {
        "req_player":player,
        "player":c_player,
        "total_battles":total_battles,
        "total_wins": total_wins,
        "total_losses": total_losses,
        "win_rate": win_rate,
        "stats":stats,
        'favorite_character': favorite_character,
        "can_edit":player == c_player,
        "n_notifs":core_views.get_notifs(c_player),
        }
    return render(request,"users/user/stats.html",context)

@login_required
def challenges(request, name):
    user = get_object_or_404(User,username = name)
    c_player = get_player(request.user)
    if not c_player:
        return redirect('/users/signin')
    player = get_object_or_404(Player,user = user)
    challenge_battles = Battle.objects.filter(initiator = c_player, type='challenge').order_by('-date_started')
    battles_data = battle_views._battles_data(c_player, challenge_battles)
    proposals = RefreeingProposal.objects.filter(battle__type = 'challenge',battle__initiator = c_player)

    stats = {
        "wins": _total_wins(player),
        "losses": _total_losses(player),
        "draws": 0
    }
    
    context = {
        "req_player": player,
        "player": c_player,
        "battles": battles_data,
        "stats": stats,
        "can_edit": player == c_player,
        "n_notifs": core_views.get_notifs(c_player),
        "proposals": battle_views._referee_proposals_data(proposals),
        }
    return render(request,"users/user/challenges.html",context)


# def get_players(request):
#     #get players without a family and who have no invite from that family
#     players = Player.objects.filter(
#         family = None
#     )
#     #players = Player.objects.all()
#     players_data = [{
#         "username": player.user.username,
#         "player":str(player),
#         "id":player.id,
#     } for player in players]
#     return JsonResponse({"status":"success", "players":players_data})

def get_members(request, family_id):
    family = Family.objects.get(id = family_id)
    members = get_family_players(family)
    members_data = [{
        "username": player.user.username,
        "player":str(player),
        "id":player.id,
    } for player in members]
    return JsonResponse({"status":"success", "members":members_data})


def family_members(_id):
    family = Family.objects.get(id = _id)
    members = get_family_players(family)
    members_data = [{
        "username": player.user.username,
        "player":str(player),
        "id":player.id,
    } for player in members]


def get_ranking(name:str):
    families = Family.objects.all() 
    sorted_families = sorted(families, key = lambda family : family.points ,reverse=True)
    for i in range(len(sorted_families)):
        if name.lower() == sorted_families[i].name.lower():
            ranking = i + 1
            if ranking == 1:
                return f'{ranking}st'
            elif ranking == 2:
                return f'{ranking}nd'
            elif ranking == 3:
                return f'{ranking}rd'
            else:
                return f'{ranking}th'
    return ""


def _families_data(families: QuerySet[Family]):
    #families = list(families)

    data = [
        {
            'id':family.id,
        "name": family.name,
        "god_father": str(family.god_father),
        'points': family.points,
        'ranking':get_ranking(family.name),
        'n_members': len(Player.objects.filter(family = family))

    } for family in families
    ]

    return data

def get_families_rankings(request):
    families = Family.objects.all()
    sorted_families = sorted(families, key = lambda family : family.points ,reverse=True)

    data = [
        {
            'id':family.id,
        "name": family.name,
        "god_father": str(family.god_father),
        'points': family.points,
        'rank':get_ranking(family.name),
        'members': len(Player.objects.filter(family = family))

    } for family in sorted_families
    ]

    return JsonResponse({'status':'success', 'families':data})

def _winner_data(battle:Battle):
    return{
            'id': battle.winner.id,
            "player":{
                'player': str(battle.winner),
                'username':battle.winner.user.username,
            },
            'profile_picture': battle.winner.profile_picture.url,
            'progress': battle.winner.progression,
            'rank': battle.winner.rank,    
            'family': battle.winner.family.name if battle.winner.family else None,
            'wins':0,
            }

def _monthly_players_ranking():
    stats = []
    for player in Player.objects.all():
        stat = {
            "wins": _total_wins(player),
            "losses": _total_losses(player),
        }
        stats.append(stat)

    sorted_stats = sorted(stats, key = lambda stat: stat['wins'], reverse=True)
    now = datetime.datetime.now()
    
    #get the first of the month for later filtering
    first_this_month = (now.replace(day = 1) - relativedelta(months=0)).replace(day = 1)
    
    #get battles whose status is finished and started after or at the first of the month

    # battles_this_month = Battle.objects.filter(
    #     Q(date_ended__gte = first_this_month) & (Q(status = 'finished'))
    #     )
    battles_this_month = Battle.objects.filter(
        Q(date_ended__gte = first_this_month)
        )
    # print("BTM:", battles_this_month)
    winners = []

    for battle in battles_this_month:
        if _winner_data(battle) not in winners:
            winners.append(_winner_data(battle))
            

    # print("TW:",winners)
    for winner in winners:
        for battle in battles_this_month:
            #update number of wins for each  winner
            if winner['id'] == battle.winner.id:
                winner['wins'] += 1 

    sorted_winners = sorted(winners, key = lambda winner: winner['wins'], reverse=True)

    return sorted_winners

@login_required
def players_ranking(request):
    #player = get_object_or_404(Player,user = request.user)
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    winners = _monthly_players_ranking()[:10]
    
    if request.method == 'POST':
        return JsonResponse({'status':'success','winners': winners })

    context = {
        'player':player,
        'n_notifs':core_views.get_notifs(player),
    }
    return render(request,'users/user/rankings.html', context)


def family_rankings(request):
    #player = get_object_or_404(Player,user = request.user)
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    
    families = Family.objects.all() 
    
    #sort families based on their points
    sorted_families = sorted(families, key = lambda family : family.points ,reverse=True)

    context = {
        'player':player,
        'n_notifs':core_views.get_notifs(player),
        'families':_families_data(sorted_families),
        
    }
    return render(request,'users/family/rankings.html', context)

@login_required
def favorites(request):
    player = get_player(request.user)
    if not player:
        return redirect('/users/signin')
    posts = []
    saved_posts = SavedPost.objects.filter(player = player).order_by('-date_added')
    for saved_post in saved_posts:
        
        posts.append(saved_post.post)

        
    context = {"posts":posts, "player":player}
    return render(request, "users/user/favorites.html",context)