from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid



class Moderator(models.Model): 
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    login_code = models.CharField(max_length = 30)

    def __str__(self):
        return f"{self.user}"