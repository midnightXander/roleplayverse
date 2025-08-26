import random
from django.db import models
from django.utils import timezone
from users.models import Player

BASIC_PASS = 2000
ALL_PASS = 5500
FREE_TEXTPAD_LIMIT = 13
def generate_custom_id():
    return str(random.randint(10000000, 99999999))


class StoryCharacter(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    character = models.JSONField()
    character_data = models.JSONField(blank=True, null=True)  # Store character data as JSON, stats
    inventory = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    subscribed = models.BooleanField(default = False)
    custom_id = models.CharField(max_length=100, blank=True, default = generate_custom_id)

    def __str__(self):
        return f"{self.player}: {self.character.get('name','character_name')}"

class StoryChallenge(models.Model):
    character = models.ForeignKey(StoryCharacter, on_delete=models.CASCADE)
    scenario = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ended = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.character} : {self.scenario[:50]}"

class StoryTextPad(models.Model):
    challenge = models.ForeignKey(StoryChallenge, on_delete=models.CASCADE)
    entry = models.TextField(default = "", null =True, blank = True)  
    text = models.TextField()    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.text[:50]}... by {self.challenge.character.character.get('name', 'Unknown')}"
    
    
class StoryPass(models.Model):
    player = player = models.ForeignKey(Player, on_delete = models.CASCADE)
    challenge = models.ForeignKey(StoryChallenge, on_delete=models.CASCADE)
    all = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player}:{self.challenge}"