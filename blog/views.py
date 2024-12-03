from django.shortcuts import render,get_object_or_404
from .models import BlogPost


def index(request):
    posts = BlogPost.objects.all().order_by('-date_added')
    return render(request, "blog/index.html",{
        'posts':posts,
    })


def blog_post(request,post_id):
    post = get_object_or_404(BlogPost, id = post_id)
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