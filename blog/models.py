from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

categories = ['News','Updates','Tutorials','Stories']

class Category(models.Model):
    """ """
    name = models.CharField(max_length=20)
    slug = models.SlugField(blank = True)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name 

    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn't already exist
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)  

class BlogPost(models.Model):
    # category = models.ForeignKey(Category, models.CASCADE, null=True)
    category = models.CharField(max_length=150, null=True)
    title = models.CharField(max_length=150)
    slug = models.SlugField(blank=True)
    leading = models.CharField(max_length=200)
    text = models.TextField()
    keywords = models.TextField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User,models.CASCADE, null=True)
    image = models.ImageField(null=True,upload_to='blog_post_covers/')
    keyword1 = models.CharField(max_length=100, null=True, blank=True)
    keyword2 = models.CharField(max_length=100, null=True, blank=True)
    keyword3 = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True, choices = [
        (i,i) for i in ['fr', 'en']
    ],  default= 'fr')
    meta_description = models.TextField(blank=True, null=True, default = "")

    views = models.IntegerField(default=0)


    def __str__(self):
        """string representation of the blog's post"""
        return self.title
    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn't already exist
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
