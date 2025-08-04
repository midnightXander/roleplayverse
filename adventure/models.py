from django.db import models
from users.models import Player
CLANS = [
    'Uchiha', 'Hyuga', 'Nara', 'Akimichi', 'Yamanaka', 'Inuzuka', 'Aburame', 'Sarutobi', 'Senju', 'Otsutsuki']


class AdventurePlayer(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    character = models.JSONField()
    character_data = models.JSONField(blank=True, null=True)  # Store character data as JSON
    inventory = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    subscribed = models.BooleanField(default = False)

    def __str__(self):
        return f"{self.player}"
    

class AdventureItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    item_type = models.CharField(max_length=50)  # e.g., 'weapon', 'armor', 'potion'
    effect = models.JSONField()  # e.g., {'health': 20, 'chakra': 10}
    rarity = models.CharField(max_length=50, default='common')  # e.g., 'common', 'rare', 'legendary'
    
    def __str__(self):
        return self.name

class CharacaterAppearance(models.Model):
    image = models.ImageField(upload_to='adventure/characters/appearances')

    def __str__(self):
        return f"Image for {self.image.name}"   

class MapZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    level_required = models.IntegerField(default=1)
    # min_level = models.IntegerField(default=1)
    # max_level = models.IntegerField(default=100)
    image = models.ImageField(upload_to='adventure/maps/zones', blank=True, null=True)
    data = models.JSONField(blank=True, null=True, help_text="Zone data in JSON format")

    def __str__(self):
        return self.name    

MISSION_TYPES = [
    ('defeat', 'Vaincre un ennemi'),
    ('collect', 'Trouver un objet'),
    ('explore', 'Explorer une zone'),
    ('survive', 'Survivre X rounds'),
    ('dialogue', 'Dialoguer avec un individu'),
]

class MissionTemplate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    long_tail_description = models.TextField()
    min_level = models.IntegerField(default=1)
    max_level = models.IntegerField(default=100)
    mission_type = models.CharField(max_length=20, choices=MISSION_TYPES)
    target = models.CharField(max_length=100, help_text="Nom de l'ennemi, de l'objet ou zone", null=True, blank=True)
    quantity = models.IntegerField(default=1)
    reward_exp = models.IntegerField(default=50)
    reward_item = models.JSONField(max_length=100, blank=True, null=True)
    rarity = models.CharField(max_length=50, default='common', choices=[('common', 'Commune'), ('rare', 'Rare'), ('epic', 'Épique')])
    zone = models.ForeignKey(MapZone, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.title}"

class PlayerMission(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    template = models.ForeignKey(MissionTemplate, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[('pending', 'En cours'), ('done', 'Terminée')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    tries = models.IntegerField(default=0)
    locked = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.player} - {self.template.title} ({self.status})"
