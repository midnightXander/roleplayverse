import random
from django.db import models
from users.models import Player

def generate_duel_code():
    numerical_part = str(random.randint(10, 999))
    alphanumerical_part = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=6))
    return alphanumerical_part


# Create your models here.
class Duel(models.Model):
    status = models.CharField(max_length=20, choices=[
        ("pending","pending"),
        ("ongoing","ongoing"),
        ("finished","finished"),
    ], default = 'pending')
    code = models.CharField(max_length=100, unique=True, default=generate_duel_code)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    log = models.TextField(blank=True, default = "[]")
    fighters = models.ManyToManyField(Player, through='DuelFighter', related_name='duel_fighters')
    winner = models.ForeignKey(Player, on_delete=models.SET_NULL,blank=True, null=True)

    def __str__(self):
        fighters = self.fighters.all()
        return f"{fighters[0]} vs {fighters[1]}  {self.started_at}"
    

class DuelFighter(models.Model):
    player = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True)
    duel = models.ForeignKey(Duel, on_delete=models.CASCADE)
    character = models.JSONField()

    def __str__(self):    
        return f"{self.player}"
    
    class Meta:
        unique_together = ('player','duel')

class DuelAction(models.Model):
    fighter = models.ForeignKey(DuelFighter, on_delete=models.SET_NULL, null=True) 
    action = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    evaluated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.fighter} - {self.action.get('name','No Action')}"


    