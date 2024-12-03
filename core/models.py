from django.db import models
from users.models import Player
from battles.models import Battle
import uuid
from django.utils import timezone

reaction_list = ["like","love","laugh","disapprove"]




class Post(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    image = models.ImageField(upload_to='posts/',blank=True,null=True)
    

    def __str__(self):
        return f"{self.author}: {self.body[:20]}..."

class SavedPost(models.Model):
    player =  models.ForeignKey(Player, on_delete=models.CASCADE)    
    post = models.ForeignKey(Post,on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField()

    def __str__(self):
        return f"{self.player}: {self.post}"


class Comment(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    body = models.TextField()
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    #replies = models.ManyToManyField()
    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=f'posts/{author}/comments/',blank=True)
    likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.author} in {self.post.body[:15]}"


#class CommenReply(models.Model):

class Reaction(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=[
        (i,i) for i in reaction_list
    ])
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type} {self.player} in {self.post}" 


class CommentReaction(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=[
        (i,i) for i in reaction_list
    ])
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    

    def __str__(self):
        return f"{self.type} {self.player} in {self.comment}"     


notification_types=["commented_post",""]
class Notification(models.Model):
    target = models.ForeignKey(Player, on_delete=models.CASCADE)
    content = models.TextField()
    url = models.CharField(max_length=100)
    date_sent = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.target}: {self.content[:10]}..."
    

class Feed(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    posts = models.ManyToManyField(Post,  through='PostFeed')
    battles = models.ManyToManyField(Battle, through='BattleFeed')

    def __str__(self):
        return f"{self.player}"

class PostFeed(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('post','feed')  


class BattleFeed(models.Model):
    battle = models.ForeignKey(Battle, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('battle','feed')            
