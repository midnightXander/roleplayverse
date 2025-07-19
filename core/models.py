from django.db import models
from users.models import Player
from battles.models import Battle
from moderator.models import Announcement
import uuid, random
from django.utils import timezone

reaction_list = ["like","love","laugh","disapprove"]

def generate_custom_id():
    return str(random.randint(10000000, 99999999))

class ContentPost(models.Model):
    TYPE_CHOICES = [('meme', 'Meme'), ('fact', 'Fun Fact')]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    image_url = models.URLField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    custom_id = models.CharField(max_length=20, default=generate_custom_id)
    reactors = models.ManyToManyField(Player, through='ContentReactor', related_name='content_reactors' ) 

    def __str__(self):
        return f"{self.title}"
    
    def most_made_reaction(self):
        # Count the reactions for this Content
        reactions = ContentReactor.objects.filter(content=self).values('type').annotate(count=models.Count('type')).order_by('-count')
        if reactions:
            return reactions[0]  # Return the most made reaction
        return None  # No reactions found

class ContentComment(models.Model):
    content = models.ForeignKey(ContentPost, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    text = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )  # For replies to comments
    date_added = models.DateTimeField(auto_now_add=True)
    reactors = models.ManyToManyField(Player, through = 'ContentCommentReactor', related_name='content_comment_reactors' ) 

    def __str__(self):
        return f"{self.author}: {self.text[:20]}..."

REACTIONS = [
        ('👍', 'Like'),
        ('👎', 'Unlike'),
        ('😂','Laugh'),
        ('😲', 'Surprise'),
        ('☹️', 'Unlike'),
    ]

class ContentReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=REACTIONS)
    content = models.ForeignKey(ContentPost, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('player','content')

class ContentCommentReactor(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

    type = models.CharField(max_length=15, choices= REACTIONS)
    date_added = models.DateTimeField(auto_now_add=True)
    comment = models.ForeignKey(ContentComment, on_delete=models.CASCADE)
    

    class Meta:
        unique_together = ('player','comment')




class Post(models.Model):
    # id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    likes = models.IntegerField(default=0)
    image = models.ImageField(upload_to='posts/',blank=True,null=True)
    #video = models.FileField(upload_to='posts/videos/',blank=True,null=True)    
    custom_id = models.CharField(max_length=20, default=generate_custom_id)

    def __str__(self):
        return f"{self.author}: {self.body[:20]}..."

class SavedPost(models.Model):
    player =  models.ForeignKey(Player, on_delete=models.CASCADE)    
    post = models.ForeignKey(Post,on_delete=models.CASCADE, null=True)
    date_added = models.DateTimeField()

    def __str__(self):
        return f"{self.player}: {self.post}"


class Comment(models.Model):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(Player, on_delete=models.CASCADE)
    body = models.TextField()
    post = models.ForeignKey(Post,on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete = models.CASCADE, blank = True, null = True)
    date_added = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to=f'posts/{author}/comments/',blank=True)
    likes = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.author} in {self.post.body[:15]}"


#class CommenReply(models.Model):

class Reaction(models.Model):
    id = models.BigAutoField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(max_length=15, choices=[
        (i,i) for i in reaction_list
    ])
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.type} {self.player} in {self.post}" 


class CommentReaction(models.Model):
    id = models.BigAutoField(primary_key=True)
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
    img_url = models.CharField(max_length=100, blank=True, null=True)
    clicked = models.BooleanField(default= False)
    
    def __str__(self):
        return f"{self.target}: {self.content[:10]}..."
    

class Feed(models.Model):
    player = models.ForeignKey(Player, on_delete = models.CASCADE)
    posts = models.ManyToManyField(Post,  through='PostFeed')
    battles = models.ManyToManyField(Battle, through='BattleFeed')
    daily_content = models.ManyToManyField(ContentPost, through='ContentFeed')
    announcements = models.ManyToManyField(Announcement, through='AnnouncementFeed')

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

class ContentFeed(models.Model):
    content = models.ForeignKey(ContentPost, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('content','feed') 

class AnnouncementFeed(models.Model):
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('announcement','feed')         

class Image(models.Model):
    image = models.ImageField()
    date_added = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        return f"{self.image.url}"        
    
    