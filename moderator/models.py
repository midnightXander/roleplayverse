from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator,MaxValueValidator
import uuid



class Moderator(models.Model): 
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    login_code = models.CharField(max_length = 30)

    def __str__(self):
        return f"{self.user}"


# class ErrorReport(models.Model):
class Announcement(models.Model):
    title = models.CharField(max_length=100, default = 'Important')
    content = models.TextField()
    image = models.ImageField(upload_to='anouncements/images')
    url = models.URLField(blank=True, null=True)
    redirect_url = models.CharField(max_length=100, blank=True, null=True)
    moderator = models.ForeignKey(Moderator, on_delete=models.CASCADE)  
    date_added = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default  = True)
    def __str__(self):
        return f"{self.content[:20]}..."