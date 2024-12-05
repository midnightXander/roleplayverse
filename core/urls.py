from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',views.index,name='index'),
    path('home',views.home,name='home'),
    path('search/<str:scope>',views.search_all,name = "search"),
    path('feed',views.get_posts,name='feed'),
    path('post/new',views.create_post, name='create_post'),
    path('post/delete/<int:id>',views.delete_post,name='delete_post'),
    path('post/modify/<int:id>',views.modify_post,name = 'modify_post'),
    path('post/<int:id>',views.post, name = 'post'),
    path('comment/<int:id>',views.comment, name = 'comment_action'),
    path('posts/<int:id>',views.post_page, name = 'post_page'),
    path('post/favorite/<int:id>',views.favorite, name = "favorite"),
    

    
    path('post/react/<int:post_id>',views.react_post,name="react"),
    path('post/comment/new/<int:post_id>',views.create_comment, name="comment"),
    path('comment/react/<int:comment_id>',views.react_comment,name="react_comment"),
    
    path('notifications', views.notifications, name='notifications'),
    path('notifications/all',views.get_notifications, name='all_notifications'),
    path('battle points',views.battle_points, name="battle_points"),

    path('rankings', views.rankings, name = 'rankings'),

]