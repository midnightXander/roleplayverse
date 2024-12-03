from django.db import models
from users.models import Player,Family
import uuid
import datetime


class Chat(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    initiator = models.ForeignKey(Player,on_delete=models.CASCADE,null=True,default=None)
    recipient = models.ForeignKey(Player,on_delete=models.CASCADE,null=True,default=None,related_name="chat_recipient")
    last_message_abbr = models.TextField()
    last_message_time_sent = models.DateTimeField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.initiator.user.username + " and " +  self.recipient.user.username

def upload_private_message_to(self,filename):
    return f"messages/private/{self.sender.user.username}_{self.receiver.user.username}/{filename}"

def upload_family_message_to(self,filename):
    return f"messages/family/{self.family.name}/{filename}"

class Message(models.Model):
    #id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    sender = models.ForeignKey(Player,on_delete=models.CASCADE)
    receiver = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True, related_name="message_receiver")
    content = models.TextField(null=True, blank=True)
    date_sent = models.DateTimeField(auto_now_add = True)
    chat = models.ForeignKey(Chat,on_delete=models.CASCADE,null=True)
    read = models.BooleanField(default=False)
    image = models.ImageField(blank=True,null=True,upload_to = upload_private_message_to)
    
    def __str__(self):
        return self.sender.user.username + " to " + self.receiver.user.username
    
class FamilyMessage(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4)
    sender = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True)
    family = models.ForeignKey(Family,on_delete=models.CASCADE,null=True, related_name="family")
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(blank=True,null=True, upload_to = upload_family_message_to)
    date_sent = models.DateTimeField(auto_now_add = True)
    

    def __str__(self):
        return self.sender.user.username + " in " + self.family.name