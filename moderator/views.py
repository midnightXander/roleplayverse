from django.shortcuts import render,get_object_or_404,redirect
from blog.models import BlogPost
from django.http import HttpResponseRedirect,Http404
from django.contrib import messages
from django.contrib.auth.models import User,auth
from django.contrib.auth import logout,login,authenticate
from django.urls import reverse
from .moderator_utility import get_moderator
import os
from dotenv import load_dotenv

load_dotenv()


def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        l_code = request.POST.get('signinCode')
        password = request.POST.get('password')

        if not email or not l_code or not password:
            messages.error(request,"Enter all fields")
            return HttpResponseRedirect(reverse("moderator:signin"))

        if l_code != os.environ.get('M_LOGIN_CODE'):
            raise Http404
        elif password != os.environ.get('M_PASSWORD'):
            raise Http404

        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request,"Wrong credentials")
            return HttpResponseRedirect(reverse("moderator:signin")) 
        
        user_auth = auth.authenticate(username = user.username,password = password)
        if user_auth is not None:
            auth.login(request,user_auth)
            return HttpResponseRedirect(reverse("moderator:index"))
        else:
            messages.error(request,"Incorrect credentials")
            return HttpResponseRedirect(reverse("moderator:signin"))
    return render(request, "moderator/signin.html")    

def index(request):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    
    return render(request, "moderator/index.html",{
        'moderator': moderator
    })
    
        

def create_post(request):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES['cover']
        leading = request.POST['leading']
        category = request.POST['category']
        new_post = BlogPost.objects.create(
            category = category,
            title = title,
            text = content,
            image = image,
            leading = leading,
        )
        new_post.save()
        return HttpResponseRedirect(reverse('moderator:index'))
    
    return render(request, "moderator/blog/create_post.html")


def edit_blog_post(request,post_id):
    moderator = get_moderator(request.user)
    if not moderator:
        raise Http404
    post = get_object_or_404(BlogPost, id = post_id)
    
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']
        image = request.FILES['cover']
        leading = request.POST['leading']
        category = request.POST['category']
        
        post.title = title
        post.text = content
        post.image = image
        post.leading = leading
        category = category
        
        post.save()
        return HttpResponseRedirect(reverse('moderator:index'))
    
    return render(request, "moderator/blog/edit_post.html",{
        'post':post
    })


