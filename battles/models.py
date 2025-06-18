from django.db import models
from users.models import Player,Family
# from events.models import Tournament
import uuid
from utility import get_characters
from django.utils import timezone
import random

def generate_custom_id():
    return str(random.randint(10000000, 99999999))

BASIC_ACTIONS = [{ "name": 'Attack', 'chakra_cost': 10, 'stamina_cost' : 10},
                    { 'name': 'Defend', 'chakra_cost': 0, 'stamina_cost': 20},
                    { 'name': 'Focus', 'chakra_cost': 0, 'stamina_cost':0 },
                    { 'name': 'Heal', 'chakra_cost': 20, 'stamina_cost' : 5 },
                    { 'name': 'Substitution', 'chakra_cost': 15, 'stamina_cost': 10},]
BATTLE_LATENCY = 20
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
BATTLE_STATUS_SET = [("waiting_refree", "En Attente d'arbitrge"), ("not_started", "Pas commencer"), ("ongoing", "En Cours"), ("finished", "Terminer")]
battle_types = ["friendly","stake","tournament","challenge"]

class Challenge(models.Model):
    sender = models.ForeignKey(Player, on_delete=models.CASCADE)
    target = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='target')
    sender_character = models.CharField(max_length=40, blank=True)
    target_character = models.CharField(max_length=40, blank=True)
    accepted = models.BooleanField(default=False)
    date_sent = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.sender} to {self.target}'


class BattleRequest(models.Model):
    
    type = models.CharField(max_length=40,choices=[
        (i,i) for i in battle_types
    ])
    sender = models.ForeignKey(Player,on_delete=models.CASCADE, null=True)
    character = models.CharField(max_length=50)
    date_sent = models.DateTimeField(auto_now_add = True)
    expiry_date = models.DateTimeField(default = timezone.now)
    hidden = models.BooleanField(default = False)
    
    def __str__(self):
        return f"{self.sender} for a {self.type} battle"
    

class SoloBattle(models.Model):
    type = models.CharField(max_length=20, choices=[
        ("training","training"),
        ("adventure","adventure"),
        ("casual","casual"),
    ], default = 'casual')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    player_character = models.JSONField()
    bot_character = models.JSONField()
    result = models.CharField(max_length=20, choices=[
        ("win","win"),
        ("lose","lose"),
        ("draw","draw"),
    ], default = 'lose')
    finished = models.BooleanField(default=False)
    date_started = models.DateTimeField(auto_now_add=True)
    date_ended = models.DateTimeField(blank=True, null=True)
    log = models.TextField(blank=True, default = "[]")

    def __str__(self):
        return f"{self.player} at {self.date_started}"

class JsonTestModel(models.Model):
    text_data = models.TextField(default="[]")
    json_data = models.JSONField() 

class Battle(models.Model):
    #id = models.BigAutoField(primary_key=True)
    custom_id = models.CharField(max_length=20, default=generate_custom_id)
    type = models.CharField(max_length=30,choices=[
        (i,i) for i in battle_types
    ])
    status = models.CharField(max_length=40,default="waiting_refree", choices=BATTLE_STATUS_SET)
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
    hidden = models.BooleanField(default = False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.award_winner_credits()

    def award_winner_credits(self):
        if self.winner:
            # Assuming Player has a method to award credits
            self.winner.award_credits(15.8)
    



    request = models.ForeignKey(BattleRequest, on_delete=models.SET_NULL, null=True, blank=True)
    
    can_send_textpad = models.BooleanField(default=False)

    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name="battle_winner", blank=True)
    viewers = models.IntegerField(default=0)
    spectators = models.ManyToManyField(Player, through='BattleSpectator', related_name='spectators')

    defeat_motif = models.CharField(max_length=50, blank=True, choices=[
        ("referee decision","Referee Decision"),
        ("latency","Latency"),
        ("abandon","Abandon"),
        ("draw","Draw"),
        ("other","Other")], default="latency")

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
    date_validated = models.DateTimeField(default = timezone.now, blank = True)
    hidden_action = models.TextField(blank=True, default="") 
    reactors = models.ManyToManyField(Player, through='TextpadReactor', related_name='reactors' ) 
    
    
    def __str__(self):
        return f"{self.owner}: {self.text[:20]}... in {self.battle}"
    
    def most_made_reaction(self):
        # Count the reactions for this TextPad
        reactions = TextpadReactor.objects.filter(textpad=self).values('type').annotate(count=models.Count('type')).order_by('-count')
        if reactions:
            return reactions[0]  # Return the most made reaction
        return None  # No reactions found

class TextPadComment(models.Model):
    textpad = models.ForeignKey(TextPad, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )  # For replies to comments
    date_added = models.DateTimeField(auto_now_add=True)
    reactors = models.ManyToManyField(Player, through = 'TextpadCommentReactor', related_name='textpad_comment_reactors' ) 

    def __str__(self):
        return f"{self.author}: {self.text[:20]}..."

REACTIONS = [
        ('👍', 'Like'),
        ('👎', 'Unlike'),
        ('😂','Laugh'),
        ('👏', 'Clapping'),
        ('😱', 'Amazed'),
    ]

class TextPadCommentReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    type = models.CharField(max_length=15, choices= REACTIONS)
    date_added = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(TextPadComment, on_delete=models.CASCADE)
    

    class Meta:
        unique_together = ('player','comment')


class TextpadReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=[
        ('👍', 'Like'),
        ('👎', 'Unlike'),
        ('😂','Laugh'),
        ('👏', 'Clapping'),
        ('😱', 'Amazed'),
    ])
    textpad = models.ForeignKey(TextPad, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','textpad')

    
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

    situation_a = models.JSONField(blank = True, null=True)
    situation_b = models.JSONField(blank = True, null=True)
    
    #fields filled by the moderator
    validated = models.BooleanField(blank=True, null=True, default=False)
    comment =  models.TextField(blank=True) 

    #dates data
    date_started = models.DateTimeField(auto_now_add=True)
    expriry_date = models.DateField(blank=True,null=True)

    def __str__(self):
        return f"{self.player.user.username} at {self.date_started}"
    





