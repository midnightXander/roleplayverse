from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',views.index,name='index'),
    path('<str:category_slug>/posts',views.category, name='category'),
    path('posts/aws-xyz-preview-<str:post_slug>',views.blog_post_preview, name='blog_post_preview'),
    path('posts/<str:post_slug>',views.blog_post, name='blog_post'),
]