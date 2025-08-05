from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid
from utility import get_characters
from django.utils import timezone
import random

rankings = ['E','D','C','B','B+','A','A+','S','SS','SSS']
FAMILYROLES = ['challenge_head','recruiter', 'casual','fighter']
referall_points = 450
MONTHLY_POINTS = 1000
ENTRY_POINTS =  1300
characters_list = get_characters()
characters_list = sorted(characters_list["playable_characters"], key = lambda item: item["name"])
ch_names = []
for ch in characters_list:
    ch_names.append(ch['name'])


PLAYER_PROFILE_PICTURES = ['1.jpg','2.jpg', '3.jpg', '4.jpg', '5.jpg', '6.png', '7.jpg', '8.jpg','9.png']

ML_STATUS = {
    "waiting referee": {
        'fr':"en attente d'arbitrage",
        'en': 'waiting referee',
    },
    'ongoing': {
        'fr':'en cours',
        'en': 'ongoing',
    }
}

# ML_STATUS.get('waiting referee').get('fr')

class PlayerDefaultImage(models.Model):
    image = models.ImageField(upload_to="players/profile_pics/")

    def __str__(self):
        return f"{self.image.name}"

class Family(models.Model):
    name = models.CharField(max_length=25)
    position = models.IntegerField(validators=[
        MinValueValidator(1)
    ])
    profile_picture = models.ImageField(upload_to="families/profile_pics/",
                                        default="default_picture_f.png")
    god_father = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    challenge_head = models.ForeignKey(User, null=True,blank=True, on_delete=models.SET_NULL,related_name='challenge_heads')
    points = models.IntegerField(default=0,validators=[
        MinValueValidator(0)
    ])
    members = models.ManyToManyField('Player', through=('FamilyMember'), related_name = 'members')
    # id = models.UUIDField(primary_key=True,default=uuid.uuid4())
    #id = models.BigAutoField(primary_key=True)
    date_created = models.DateField(auto_now_add=True)
    
    class Meta():
        verbose_name_plural = 'Families'

    def __str__(self):
        return  self.name

#Badges to be added in the db manually by the admin 
class Badge(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.title}'

class FamilyBadge(models.Model):
    title = models.CharField(max_length=30)

    def __str__(self):
        return f'{self.title}'

class Achievement(models.Model):
    title = models.CharField(max_length=50)    
    def __str__(self):
        return f'{self.title}'
    
class Event(models.Model):
    title = models.CharField(max_length=100)    
    description = models.TextField(blank = True)
    def __str__(self):
        return f'{self.title}'

def rank_index(rank):
        for i in range(len(rankings)):
            if rank == rankings[i]:
                index = i
        return index


    

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(default='E',max_length=3,choices=[
        (i,i) for i in rankings
    ])
    profile_picture = models.ImageField(upload_to="players/profile_pics/",  
                                        default = "blank-profile-picture.png"
                                        )
    family = models.ForeignKey(Family,on_delete=models.SET_NULL,null=True,blank=True,default=None)
    #family_pk = models.IntegerField(null=True, blank = True, default = None) #To reference the family 
    nickname = models.CharField(max_length=30,blank=True,null=True)
    gender = models.CharField(default='male', max_length=10, choices=[
        (i,i) for i in ['male','female']
    ])
    bio = models.CharField(max_length=60 ,blank=True)
    country = models.CharField(max_length=80)
    p_character = models.CharField(default= ch_names[0],max_length=30,choices=[
        (i,i) for i in ch_names
    ])
    authorized_to_fight = models.BooleanField(default=False,blank=True)
    can_create_family = models.BooleanField(default=False,blank=True)

    achievements = models.ManyToManyField(Achievement, through=('PlayerAchievement'))
    events = models.ManyToManyField('Event', through='PlayerEvent')

    language = models.CharField(default = 'fr', max_length=20)
    battle_points = models.IntegerField(default=1000)
    badges = models.ManyToManyField(Badge, through='PlayerBadge')
    progression = models.IntegerField(default=0, validators=[
        MinValueValidator(0),MaxValueValidator(100)
    ])

    referall_code = models.CharField(max_length=80)
    # recover_code = models.CharField(max_length=50)

    date_points_added = models.DateField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    rp_credits = models.DecimalField(default=0,  max_digits=10, decimal_places=2)
    ip_adress = models.CharField(max_length=50, blank=True, null=True)
    godfather = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.update_rank()

    def update_rank(self, rankings = rankings, force = False):
        """Updates the rank of the player based on the progression and current rank"""
        r_index = rank_index(self.rank)
        print(r_index)
        if r_index < len(rankings):
            if self.progression >= 100:
                self.rank = rankings[r_index + 1]
                self.progression = 0
            if self.progression < 0:
                self.progression = 0
            if force:
                self.rank = rankings[r_index + 1]        
        else:
            print(f"{self.user.username} is at the max ranking already")        
        self.save() 

    def unread_messages(self):
        from chat.models import Message
        from chat.views import _get_family_unreads,_get_private_messages_unreads
        """Returns the number of unread messages for the player"""
        private_messages = Message.objects.filter(receiver = self, read = False).count()
        family_messages = _get_family_unreads(self)
            
        return  private_messages + family_messages
        
        

    def add_points(self, points:int, monthly_points:bool = False):
        """Adds points(Battle tokens) to the player"""

        self.battle_points += points
        if monthly_points: self.date_points_added = timezone.now()

        self.save()

    def award_credits(self, credits):
        self.rp_credits = self.rp_credits + credits
        self.save() 

    def notifs(self):
        player_notifs = PlayerNotification.objects.filter(target= self, read = False)
        from core.models import Notification
        from battles.models import Challenge
        notifs = Notification.objects.filter(target = self, read = False)
        challenges = Challenge.objects.filter(target = self)
        n_notifs = len(player_notifs) + len(notifs) + len(challenges)

        if n_notifs == 0:
            return ""
        if n_notifs>9:
            return "9+"
        else:
            return f"{n_notifs}"     
        


    def __str__(self):
        # referee_badge = Badge.objects.filter(title = 'Referee')
        # if referee_badge in self.badges.all():
        #     return  self.user.username + "⚖" 
        if self.family:
            return self.user.username + f"({self.family})"
        else:
            return self.user.username


class PasswordRecoveryCode(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    key = models.CharField(max_length=30, primary_key=True)

    def __str__(self):
        return f"{self.player}" 

class PlayerBadge(models.Model):
    player = models.ForeignKey(Player, on_delete= models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','badge')

notification_types = ["invite","request","private_message","new_textpad","family_message",
                      "refused_request","denied_invite",
                      "battle_accepted","refree_proposal","textpad_accepted","textpad_refused",'battle_started','family_points','tournament_started',]
class PlayerNotification(models.Model):
    notif_type = models.CharField(max_length=30)
    sender = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True,blank=True)
    target = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True,blank=True,related_name="player_notifications")
    date_sent = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField(blank=True,null=True)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL,null=True)
    # content = models.TextField(blank=True)
    # url = models.CharField(null=True, blank=True, max_length=100)
    # #battle = models.ForeignKey(Battle, on_delete=models.SET_NULL,null=True,blank=True)
    # battle_id = models.UUIDField(blank = True, null = True)
    read = models.BooleanField(default=False)

    def __str__(self):
        
        if self.notif_type == "invite":
            return self.notif_type + f" to join {self.family} family from {self.sender}"
        elif self.notif_type == "request":    
            return self.notif_type + f" to join {self.family} from " + self.sender.user.username
        elif self.notif_type == "private_message":
              return f"New Message" + " from " + self.sender.user.username
        elif self.notif_type == "family_message":
              return f"New Message in {self.family}" + " from " + self.sender.user.username
        elif self.notif_type == "textpad":
              return f"New textpad in battle" + " from " + self.sender.user.username
        else:
            return f"New {self.notif_type}" + " from " + self.sender.user.username
        

class PlayerStat(models.Model):
    player = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True)
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)      

    def __str__(self):
        return f"{self.player}: {self.wins} wins, {self.losses} losses, {self.draws} draws "  

class RefreeStat(models.Model):
    player = models.ForeignKey(Player,on_delete=models.CASCADE)
    fairness = models.IntegerField(default=1)
    communication = models.IntegerField(default=1)
    timeliness = models.IntegerField(default=1)
    overall = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.player}"    
    
 



class PlayerAchievement(models.Model):
    player  = models.ForeignKey(Player, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.SET_NULL, null = True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','achievement')

class PlayerEvent(models.Model):
    player  = models.ForeignKey(Player, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null = True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','event')


class FamilyMember(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    family = models.ForeignKey(Family, on_delete=models.SET_NULL, null = True)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, choices = [
        (i,i) for i in FAMILYROLES
    ], default = 'casual')

    class Meta:
        unique_together = ('player', 'family')


