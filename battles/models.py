from django.db import models
from users.models import Player,Family
# from events.models import Tournament
import uuid
from utility import get_characters
from django.utils import timezone

BATTLE_LATENCY = 5
f_request_cost = 250
s_request_cost = 350
request_cost = 350
accept_cost = 150
CHALLENGE_COST = 400
tournament_cost = 500

characters_list = get_characters()
characters_list = sorted(characters_list["playable_characters"], key = lambda item: item["name"])
ch_names = []
for ch in characters_list:
    ch_names.append(ch['name'])

battle_status = ["waiting_refree","not_started","ongoing", "finished"]
battle_types = ["friendly","stake","tournament","challenge"]

class Challenge(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE)
    target = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='target')
    sender_character = models.CharField(max_length=40, blank=True)
    target_character = models.CharField(max_length=40, blank=True)
    accepted = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.sender} to {self.target}'


class BattleRequest(models.Model):
    #id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    type = models.CharField(max_length=40,choices=[
        (i,i) for i in battle_types
    ])
    sender = models.ForeignKey(Player,on_delete=models.CASCADE, null=True)
    character = models.CharField(max_length=50)
    date_sent = models.DateTimeField(auto_now_add = True)
    expiry_date = models.DateTimeField(default = timezone.now)

    
    def __str__(self):
        return f"{self.sender} for a {self.type} battle"
    


class Battle(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    type = models.CharField(max_length=30,choices=[
        (i,i) for i in battle_types
    ])
    status = models.CharField(max_length=40,default="waiting_refree", choices=(
        (i,i) for i in battle_status ))
    flags = models.TextField(blank=True)        
    initiator = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)

    i_character = models.CharField(max_length=30,blank=True,choices=(
        (i,i) for i in ch_names ))
    o_character = models.CharField(max_length=30, blank=True,choices=(
        (i,i) for i in ch_names ))

    opponent = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name="battle_challenger")
    refree = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name="battle_refree")
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(blank=True,null=True)

    request = models.ForeignKey(BattleRequest, on_delete=models.SET_NULL, null=True)
    
    can_send_textpad = models.BooleanField(default=False)

    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name="battle_winner", blank=True)
    
    spectators = models.ManyToManyField(Player, through='BattleSpectator', related_name='spectators')

    def __str__(self):
        return f'{self.type} {self.initiator} vs {self.opponent} '

class BattleSpectator(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    date_viewed = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','battle')




class RefereeRating(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE,null = True)
    fairness = models.IntegerField(default=1)
    timeliness = models.IntegerField(default=1)
    communication = models.IntegerField(default=1)
    comment = models.TextField()
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.player}: {self.fairness}-{self.timeliness}-{self.communication}"



class Refree(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    rating = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.player}"

rule_types = ["standard_rule","specific_rule1","specific_rule2"]
class Rule(models.Model):
    type = models.CharField(max_length=30)
    text = models.TextField()
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.text}'

   

class BattleAcceptor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    request = models.ForeignKey(BattleRequest, on_delete=models.CASCADE, null=True)
    character = models.CharField(max_length=30)
    date_sent = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.player} accepted request from {self.request}"

class RefreeingProposal(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE, null=True)
    
    def __str__(self):
        return f"{self.player} wants to referee {self.battle}"

class TextPad(models.Model):
    #status = models.CharField(max_length = 20)
    owner = models.ForeignKey(Player, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    valid =models.BooleanField(default=False)
    battle = models.ForeignKey(Battle, on_delete=models.SET_NULL, null=True)
    refree_comment = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.owner}: {self.text[:20]}... in {self.battle}"


    
#class TextPadComment    






situations_1 = ['battles/situations/1.jpg','battles/situations/2.jpg','battles/situations/3.jpg']
situations_2 = ['battles/situations/4.jpg', 'battles/situations/5.jpg', 'battles/situations/6.jpg']

class RefreeTest(models.Model):
    #only required fields
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    quizScore = models.IntegerField()

    #blank fields to be filled after the 2nd step of the test
    situation1 = models.ImageField(blank=True,choices= [
        (i,i) for i in situations_1
    ])
    verdict1 = models.TextField(blank=True)
    situation2 = models.ImageField(blank=True, choices= [
        (i,i) for i in situations_2
    ])
    verdict2 = models.TextField(blank=True)
    
    #fields filled by the moderator
    validated = models.BooleanField(blank=True, null=True, default=False)
    comment =  models.TextField(blank=True) 

    #dates data
    date_started = models.DateTimeField(auto_now_add=True)
    expriry_date = models.DateField(blank=True,null=True)

    def __str__(self):
        return f"{self.player.user.username} at {self.date_started}"
    




