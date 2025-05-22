from django.db import models
from users.models import Player
from django.contrib.auth.models import User
from battles.models import Battle
import uuid, random
from django.utils import timezone


class AdClick(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.JSONField()
    # url = models.CharField(max_length = 100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} at {self.date}'
