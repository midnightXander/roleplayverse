from django.shortcuts import render,get_object_or_404, redirect

from moderator.models import Moderator
from users.users_utility import get_client_ip_and_country
from .models import BlogPost, BlogPostViewer, Category
from ipware import get_client_ip

def index(request):
    posts = BlogPost.objects.filter(visible = True).order_by('-date_added')
    categories = Category.objects.all()
    # for post in posts:
    #     post.category = None
    #     post.save()
    is_moderator = False
    if request.user.is_authenticated:
        is_moderator = Moderator.objects.filter(user=request.user).exists()
    return render(request, "blog/index.html", {
        'posts':posts,
        'categories':categories,
        "is_moderator": is_moderator
    })

def _update_post_viewers(request, post:BlogPost):
    
    user = None
    if request.user.is_authenticated:
        user = request.user
    viewer_ip, country = get_client_ip_and_country(request)
    BlogPostViewer.objects.update_or_create(
        user=user,
        post=post,
        defaults={
            'viewer_ip': viewer_ip,
            'country': country,
        }
    )

def blog_post(request,post_slug):
    post = BlogPost.objects.filter(slug = post_slug).first()
    _update_post_viewers(request, post)
    categories = Category.objects.all()
    if not post:
        return redirect('/blog')
        # return render(request, "blog/404.html",{})
    post.views += 1
    post.save()
    
    if request.method == 'POST':
        pass
    return render(request, "blog/post.html",{
        'post':post,
        'categories':categories,
    })

def blog_post_preview(request,post_slug):
    categories = Category.objects.all()
    post = BlogPost.objects.filter(slug = post_slug).first()
    return render(request, "blog/post_preview.html",{
        'categories':categories,
        'post':post,
    })



def category(request,category_slug):
    category = Category.objects.filter(slug = category_slug).first()
    categories = Category.objects.all()
    if not category:
        return redirect('/blog')
        # return render(request, "blog/404.html",{})
    posts = BlogPost.objects.filter(category = category, visible=True).order_by('-date_added')
    if request.method == 'POST':
        pass
    return render(request, "blog/category.html",{
        'posts':posts,
        'category' : category,
        'categories':categories,
    })


def createPost(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_slug = request.POST.get('category')
        category = Category.objects.filter(slug=category_slug).first()
        if not category:
            return redirect('/blog')
        post = BlogPost.objects.create(title=title, content=content, category=category)
        return redirect('blog:blog_post', post_slug=post.slug)
    return render(request, "blog/create_post.html")