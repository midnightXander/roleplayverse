from django.urls import path
from . import views

app_name = 'moderator'

urlpatterns = [
    path('',views.index,name='index'),
    path('signinxyz',views.signin, name = 'signin'),
    path('blog/create',views.create_post,name = 'create_post'),
    path('blog/edit/<int:post_id>',views.edit_blog_post,name = 'edit_post'),
]