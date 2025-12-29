import random
from django.db import models
from django.utils import timezone
from users.models import Player

BASIC_PASS = 2000
ALL_PASS = 5500
FREE_TEXTPAD_LIMIT = 20
NO_ADS_PASS = 8500
def generate_custom_id():
    return str(random.randint(10000000, 99999999))

REACTIONS = [
        ('👍', 'Like'),
        ('👎', 'Unlike'),
        ('😂','Laugh'),
        ('👏', 'Clapping'),
        ('😱', 'Amazed'),
    ]

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
    readers = models.ManyToManyField(Player, through='StoryReader', related_name='storyreaders' ) 
    reads = models.PositiveIntegerField(default = 0)


    def __str__(self):
        return f"{self.character} : {self.scenario[:50]}"

class StoryReader(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)
    story = models.ForeignKey(StoryChallenge, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player','story')    

class StoryTextPad(models.Model):
    challenge = models.ForeignKey(StoryChallenge, on_delete=models.CASCADE)
    entry = models.TextField(default = "", null =True, blank = True)  
    text = models.TextField()    
    data = models.JSONField(blank=True, null=True)  # Store additional data as JSON, e.g., images
    created_at = models.DateTimeField(auto_now_add=True)

    reactors = models.ManyToManyField(Player, through='StoryTextpadReactor', related_name='storyreactors' ) 
    player = models.ForeignKey(Player, on_delete=models.CASCADE,blank=True, null=True)

    def __str__(self):
        self.player = self.challenge.character.player
        print(self.player)
        self.save()
        return f"{self.text[:50]}... by {self.challenge.character.character.get('name', 'Unknown')}"
    
    # def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
    #     return super().save(force_insert, force_update, using, update_fields)
    
    
    
    
    def most_made_reaction(self):
        # Count the reactions for this TextPad
        reactions = StoryTextpadReactor.objects.filter(textpad=self).values('type').annotate(count=models.Count('type')).order_by('-count')
        if reactions:
            return reactions[0]  # Return the most made reaction
        return None  # No reactions found
    




class StoryTextPadComment(models.Model):
    textpad = models.ForeignKey(StoryTextPad, on_delete=models.CASCADE, related_name="story_comments")
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )  # For replies to comments
    date_added = models.DateTimeField(auto_now_add=True)
    reactors = models.ManyToManyField(Player, through = 'StoryTextpadCommentReactor', related_name='story_textpad_comment_reactors' ) 

    def __str__(self):
        return f"{self.author}: {self.text[:20]}..."

class StoryTextPadCommentReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    type = models.CharField(max_length=15, choices= REACTIONS)
    date_added = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(StoryTextPadComment, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('player','comment')


class StoryTextpadReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=[
        ('👍', 'Like'),
        ('👎', 'Unlike'),
        ('😂','Laugh'),
        ('👏', 'Clapping'),
        ('😱', 'Amazed'),
    ])
    textpad = models.ForeignKey(StoryTextPad, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','textpad')

class StoryPass(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    challenge = models.ForeignKey(StoryChallenge, on_delete=models.CASCADE)
    all = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player}:{self.challenge}"
    
class NoAdsPass(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player} - No Ads Pass"

