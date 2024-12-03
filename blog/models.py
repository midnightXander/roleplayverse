from django.db import models
from django.contrib.auth.models import User


categories = ['News','Updates','Tutorials']

class BlogPost(models.Model):
    category = models.CharField(choices = [
        (i,i) for i in categories
    ], max_length=30)
    title = models.CharField(max_length=20)
    leading = models.CharField(max_length=60)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User,models.CASCADE, null=True)
    image = models.ImageField(null=True,upload_to='blog_post_covers/')

    def __str__(self):
        """string representation of the blog's post"""
        return self.title
