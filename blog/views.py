from django.shortcuts import render,get_object_or_404

from moderator.models import Moderator
from .models import BlogPost


def index(request):
    posts = BlogPost.objects.all().order_by('-date_added')
    is_moderator = False
    if request.user.is_authenticated:
        is_moderator = Moderator.objects.filter(user=request.user).exists() 
    return render(request, "blog/index.html",{
        'posts':posts,
        "is_moderator": is_moderator
    })


def blog_post(request,post_id):
    post = get_object_or_404(BlogPost, id = post_id)
    post.views += 1
    post.save()
    
    if request.method == 'POST':
        pass
    return render(request, "blog/post.html",{
        'post':post
    })



def category(request,category):
    posts = BlogPost.objects.filter(category = category)
    if request.method == 'POST':
        pass
    return render(request, "blog/category.html",{
        'posts':posts
    })


def createPost(request):
    if request.method == 'POST':
        pass