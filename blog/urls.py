from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',views.index,name='index'),
    path('<str:category>/posts',views.category, name='category'),
    path('posts/321<int:post_id>',views.blog_post, name='blog_post'),
]