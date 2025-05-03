from django.db import models
from django.contrib.auth.models import User


categories = ['News','Updates','Tutorials']
#new category: 'Stories'

class BlogPost(models.Model):
    category = models.CharField(choices = [
        (i,i) for i in categories
    ], max_length=30)
    title = models.CharField(max_length=150)
    leading = models.CharField(max_length=200)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User,models.CASCADE, null=True)
    image = models.ImageField(null=True,upload_to='blog_post_covers/')
    keyword1 = models.CharField(max_length=100, null=True, blank=True)
    keyword2 = models.CharField(max_length=100, null=True, blank=True)
    keyword3 = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True, choices = [
        (i,i) for i in ['fr', 'en']
    ])
    meta_description = models.CharField(max_length=300, null=True, blank=True)


    def __str__(self):
        """string representation of the blog's post"""
        return self.title
