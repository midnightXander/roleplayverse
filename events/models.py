from django.db import models
from users.models import Player
from battles.models import Battle
from django.utils import timezone
from random import randint
import uuid
#from battles.models import Battle


class TournamentRequest(models.Model):
    name = models.CharField(max_length=30)
    creator = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(default=timezone.now)
    n_participants = models.IntegerField(
    #     choices=[
    #     (i,i) for i in [4,8,16]
    # ]
    )
    rules = models.TextField()

    def __str__(self):
        return f"{self.name}"


tournament_status = ['registering','not_started','ongoing','finished']
tournament_restrictions = [
    'specific_characters',
    'jutsu_types',

] 
tournament_covers = ['1.png','2.jpg','3.jpg','4.jpg','5.jpg','6.jpg']

def tournament_upload_to(self, filename):
    return f'{self.name}/{filename}'

class Tournament(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    name = models.CharField(max_length=30, unique=True)
    
    n_participants = models.IntegerField(
    #     choices=[
    #     (i,i) for i in [4,8,16]
    # ]
    )
    creator = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True,related_name='creator')
    start_date = models.DateField(default=timezone.now)
    status = models.CharField(default=tournament_status[0],max_length=20,choices=[
        (i,i) for i in tournament_status
    ])

    participation_cost = models.IntegerField(default=500)
    reward = models.IntegerField(default=2000)

    rules = models.TextField(default='rules')
    date_created = models.DateField(auto_now_add = True )
    cover = models.ImageField(default = f'tournaments/covers/{tournament_covers[randint(0, len(tournament_covers)-1)]}',upload_to=tournament_upload_to)
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name='winner')
    
    #restrictrions: select from a list of restrictions like 'only players from a particular country can 
    # participate' then the system will apply the restriction automatically making sure it is respected
    refrees = models.ManyToManyField(Player,through='RefreeTournament')
    fighters = models.ManyToManyField(Player, through='FighterTournament',related_name='fighters')
    battles = models.ManyToManyField(Battle, through='TournamentBattle')
    

    def __str__(self):
        return f'{self.name}'
    
class FighterTournament(models.Model):
    fighter = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    character = models.CharField(max_length=30)
    round = models.IntegerField(default=1)

    class Meta:
        unique_together = ('fighter','tournament')


class RefreeTournament(models.Model):
    refree = models.ForeignKey(Player, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    class Meta:
        #ensures a refree can't be registered twice for the same tournament
        unique_together = ('refree','tournament')

class TournamentBattle(models.Model):
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round = models.IntegerField(default=1)

    class Meta:
        unique_together = ('battle', 'tournament')



#For tournamnents
class Round(models.Model):
    number = models.IntegerField()
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    battles = models.ManyToManyField(Battle, through="RoundBattle")

    def __str__(self):
        return f"Round {self.number} in {self.tournament}"

class RoundBattle(models.Model):
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    round = models.ForeignKey(Round, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('battle','round')




class TournamentRefreeRequest(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    date_sent = models.DateTimeField(auto_now_add=True)
    
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.player} wants to refree in {self.tournament}"