from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid
from utility import get_characters
from django.utils import timezone

rankings = ['E','D','C','B','B+','A','A+','S','SS','SSS']

referall_points = 150
MONTHLY_POINTS = 1000
ENTRY_POINTS =  10300
characters_list = get_characters()
characters_list = sorted(characters_list["playable_characters"], key = lambda item: item["name"])
ch_names = []
for ch in characters_list:
    ch_names.append(ch['name'])

class Family(models.Model):
    name = models.CharField(max_length=25)
    position = models.IntegerField(validators=[
        MinValueValidator(1)
    ])
    profile_picture = models.ImageField(upload_to="families/profile_pics/",default="default_picture_f.png")
    god_father = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100,blank=True)
    challenge_head = models.ForeignKey(User, null=True,blank=True, on_delete=models.SET_NULL,related_name='challenge_heads')
    points = models.IntegerField(default=0,validators=[
        MinValueValidator(1)
    ])
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4())
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

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rank = models.CharField(default='E',max_length=3,choices=[
        (i,i) for i in rankings
    ])
    profile_picture = models.ImageField(upload_to="players/profile_pics/",  default="blank-profile-picture.png")
    family = models.ForeignKey(Family,on_delete=models.SET_NULL,null=True,blank=True,default=None)
    nickname = models.CharField(max_length=30,blank=True,null=True)
    gender = models.CharField(default='male', max_length=10, choices=[
        (i,i) for i in ['male','female']
    ])
    bio = models.CharField(max_length=60 ,blank=True)
    country = models.CharField(max_length=80,choices=[
        (i,i) for i in ["Cameroon","Congo"]
    ])
    p_character = models.CharField(default= ch_names[0],max_length=30,choices=[
        (i,i) for i in ch_names
    ])
    authorized_to_fight = models.BooleanField(default=False,blank=True)
    can_create_family = models.BooleanField(default=False,blank=True)

    achievements = models.ManyToManyField(Achievement, through=('PlayerAchievement'))

    language = models.CharField(default = 'en', max_length=20)
    battle_points = models.IntegerField(default=1000)
    badges = models.ManyToManyField(Badge, through='PlayerBadge')
    progression = models.IntegerField(default=0, validators=[
        MinValueValidator(0),MaxValueValidator(100)
    ])

    referall_code = models.CharField(max_length=80)
    # recover_code = models.CharField(max_length=50)

    date_joined = models.DateField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
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

