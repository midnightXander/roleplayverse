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
        date_sent = last_textpad.date_sent
        difference = now - date_sent
        seconds = difference.seconds
        hours = seconds // 3600

        #the winner here is the owner of the last textpad and the loser is the other player
        winner = last_textpad.owner
        loser = battle.initiator if winner == battle.opponent else battle.opponent
        
        

        if hours == BATTLE_LATENCY-1:
            #SEND EMAIL ALERTING PLAYER he is going to lose 
            #Send_email()
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

            progress =  player_progress(battle=battle,loser_rank = loser.rank)
            winner.progression +=  progress
            
            #update the player's rank if progression reached 100%
            update_rank(winner)
            update_points(family = winner.family, battle=battle, member_progress=progress)

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
            win_notif.save()

            lose_notif = Notification.objects.create(
                        target = loser,
                        url = f'/battles/battle_room/{battle.id}',
                        content = f"Tu as perdu ton combat contre {winner} par latence"
                    )
            lose_notif.save()  
            
            referee_notif = Notification.objects.create(
                        target = battle.refree,
                        url = f'/battles/battle_room/{battle.id}',
                        content = f"Le combat {winner} vs {loser} que tu arbitrais a été terminé par latence"
                    )
            referee_notif.save()  
            
            

@shared_task
def delete_expired_notifications():
    print("delete notif")

@shared_task
def add_monthly_points():
    for player in Player.objects.all():
        #REVIEW THIS, SHOULD BE WITH DAYS
        joined_day = player.date_joined.day
        current_day = timezone.now().day

        if joined_day == current_day:
            add_points(player, MONTHLY_POINTS)
            
            #send email to notify player got monthly points  / or notify normally?      

@shared_task
def newsletter():
    print("Send email to user")