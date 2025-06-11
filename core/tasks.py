from celery import shared_task
from .models import *
from core.models import *
from users.models import *
from battles.models import *
from battles.views import update_rank,update_points,player_progress
from events.views import _update_round
from django.utils import timezone
from core.views import add_points
from datetime import datetime
from . import emails
from api.utility import send_push_notification
from api.models import PushSubscription
import praw,os
from dotenv import load_dotenv

load_dotenv()
# @shared_task
# def delete_expired_instances():
#     now = timezone.now()
#     expired_instances = Notification.objects.filter(expiry_date__lte=now)
#     expired_instances.delete()


#TASKS
#DELETE referee tests after 10 days of creation
#latency for battles to be at 3h-6h with email notifs to be sent one hour before the deadline(if the user is not online recently) 
#Award the top monthly players



@shared_task
def delete_referee_tests():
    now = timezone.now()
    all_tests = RefreeTest.objects.all()
    for test in all_tests:
        if now.day - test.date_started.day >= 5:
            
            test.delete()
            new_notif = Notification.objects.create(
                target = test.player,
                url = '/battles/refrees/new_refree',
                content = "Tu peux a nouveau faire le test d'arbitrage, applique toi cette fois!"
            )
            new_notif.save()
            #SEND EMAIL/NOTIFICATION TO PLAYER TELLING HE CAN TAKE A NEW TEST

@shared_task
def manage_battles_latency():
    print("checking battles...")
    battles = Battle.objects.filter(status = 'ongoing')
    for battle in battles:
        now = timezone.now()
        last_textpad = TextPad.objects.filter(battle = battle).last()
        date_sent = last_textpad.date_validated
        difference = now - date_sent
        seconds = difference.seconds
        hours = seconds // 3600

        #the winner here is the owner of the last textpad and the loser is the other player
        winner = last_textpad.owner
        loser = battle.initiator if winner == battle.opponent else battle.opponent
        
        

        if hours == BATTLE_LATENCY - 4 and last_textpad.valid:
            #SEND EMAIL ALERTING PLAYER he is going to lose 
            #Send_email()
            
            send_push_notification(
                PushSubscription.objects.filter(user=loser.user).last(),
                {
                    "title": "Alerte de latence",
                    "body": f"Tu es sur le point de perdre ton combat contre {winner} par latence! Fais ton pavé maintenant!",
                    "url": f"/battles/battle_room/{battle.id}",
                    "action": "open_battle",
                    'icon' : '/static/images/logo/logo_1.png',
                },
                loser.user,
                )
            try: 
                emails.send_email(
                    recipient_email = loser.user.email,
                    title = "Alerte de latence",
                    subject = "Tu es sur le point de perdre ton combat par latence!",
                    body = f"""
                    <h2>Hey {loser},</h2>
                    <p>Tu es sur le point de perdre ton combat contre {winner} par latence!</p>
                    <p>Fais ton pavé maintenant!</p>
                    <a href="/battles/battle_room/{battle.id} class='button'">Accéder au combat</a>
                    """,
                    #language = loser.user.language
                )
            except Exception as e:
                print(f"Email error: {e}")

            alert_notif = Notification.objects.create(
                    target = loser,
                    url = f'/battles/battle_room/{battle.id}',
                    content = f"Tu es sur le point de perdre le combat contre {winner} par latence, fais ton pavé maintenant!!"
                )
            alert_notif.save() 
            
            
            
        elif hours >= BATTLE_LATENCY and last_textpad.valid:
            #END BATTLE
            battle.winner = winner 
            battle.status = battle_status[3]
            battle.date_ended = datetime.now()
            battle.defeat_motif = "latency"

            progress =  player_progress(battle=battle,loser_rank = loser.rank)
            winner.progression +=  progress
            
            #update the player's rank if progression reached 100%
            update_rank(winner)
            update_points(family = winner.family, battle=battle, member_progress=progress)
            winner.award_credits(40)

            winner.save()
            last_textpad.save()
            battle.save()
                
            if(battle.type == 'tournament'):
                _update_round(battle)
            battle.can_send_textpad = False
            
            battle.save()    
            win_notif = Notification.objects.create(
                        target = winner,
                        url = f'/battles/battle_room/{battle.id}',
                        content = f"Tu as été declaré  vainqueur de ton combat contre {loser} par latence"
                        )
            send_push_notification(
                PushSubscription.objects.filter(user=winner.user).last(),
                {
                    "title": "Tu as remporte ton combat",
                    "body": f"Tu as été declaré  vainqueur de ton combat contre {loser} par latence",
                    "url": f"https://roleplayverse.live",
                    'icon' : '/static/images/logo/logo_1.png',
                },
                winner.user,
                ) 
            win_notif.save()

            lose_notif = Notification.objects.create(
                        target = loser,
                        url = f'/battles/battle_room/{battle.id}',
                        content = f"Tu as perdu ton combat contre {winner} par latence"
                    )
            lose_notif.save()  
            send_push_notification(
                PushSubscription.objects.filter(user=loser.user).last(),
                {
                    "title": "Tu as perdu ton combat",
                    "body": f"Tu as perdu ton combat contre {winner} par latence",
                    "url": f"https://roleplayverse.live/notifications",
                    'icon' : '/static/images/logo/logo_1.png',
                },
                loser.user,
            )
            
            referee_notif = Notification.objects.create(
                        target = battle.refree,
                        url = f'/battles/battle_room/{battle.id}',
                        content = f"Le combat {winner} vs {loser} que tu arbitrais a été terminé par latence"
                    )
            referee_notif.save()  
            send_push_notification(
                PushSubscription.objects.filter(user=battle.refree.user).last(),
                {
                    "title": "Le combat a été terminé par latence",
                    "body": f"Le combat {winner} vs {loser} que tu arbitrais a été terminé par latence",
                    "url": f"https://roleplayverse.live/notifications",
                    'icon' : '/static/images/logo/logo_1.png',
                },
                battle.refree.user,
            )
            
            

@shared_task
def delete_expired_notifications():
    print("delete notif")

@shared_task
def add_monthly_points():
    for player in Player.objects.all():
        #REVIEW THIS, SHOULD BE WITH DAYS

        last_day_added = player.date_points_added.day
        current_day = timezone.now().day

        days_difference = timezone.now() - player.date_points_added

        if days_difference.days == 30:
            #add_points(player, MONTHLY_POINTS)
            #player.date_points_added = timezone.now()
            player.add_points(MONTHLY_POINTS, True)
            
            #send email to notify player got monthly points  / or notify normally?
            Notification.objects.create(
                target = player,
                url = f'/users/{player.user.username}',
                content = f"Tu as reçu {MONTHLY_POINTS} de jetons mensuels!"
            )
            send_push_notification(
                PushSubscription.objects.filter(user=player.user).last(),
                {
                    "title": "Jetons mensuels",
                    "body": f"Tu as reçu tes jetons mensuels de {MONTHLY_POINTS}!",
                    "url": f"https://roleplayverse.live/users/{player.user.username}",
                    'icon' : '/static/images/logo/logo_1.png',
                },
                player.user,
                )   

@shared_task
def fetch_daily_content():
    REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    # print(REDDIT_CLIENT_SECRET, REDDIT_CLIENT_ID)
    try:
        reddit = praw.Reddit(
            client_id= REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent='RPV Meme Bot'
        )
        subreddit = reddit.subreddit('narutomemes')
        post_count = 0
        for post in subreddit.hot(limit=50):
            if not post.stickied and post.url.endswith(('.jpg', '.png', '.gif', 'jpeg')):
                if not ContentPost.objects.filter(image_url=post.url).exists() and post_count <= 5:
                    ContentPost.objects.create(
                        type = 'meme',
                        title=post.title,
                        image_url=post.url,
                        #reddit_score=post.score
                    )
                    ContentPost.save()
                    post_count = post_count + 1
                    if post_count == 5: return

        #notify all suscribed players for new memes 
        # suscriptions = PushSubscription.objects.all()
        users = User.objects.all()
        users = users.order_by('?')[:50] #get 15 random users
        for user in users:
            send_push_notification(PushSubscription.objects.filter(user = user).last(),{
                "title": "De Nouveaux Meme sont disponible 🤩",
                "body": f"Tous les jours, de nouveaux memes sont ajouté a ton fil pour une bonne séance de rire, en voila de nouveaux",
                "url": f"https://roleplayverse.live/home",
                'icon' : '/static/images/logo/logo_1.png',
            }, user)


                    
    except Exception as ex:
        print(f"Could not Fetch reddit posts, err: {ex}")                               

@shared_task
def newsletter():
    print("Send email to user")