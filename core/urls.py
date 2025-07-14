from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('',views.index,name='index'),
    path('onboarding',views.onboarding,name='onboarding'),
    path('home',views.home,name='home'),
    path('search/<str:scope>',views.search_all,name = "search"),
    path('feed',views.get_posts,name='feed'),
    path('post/new',views.create_post, name='create_post'),
    path('post/delete/<int:id>',views.delete_post,name='delete_post'),
    path('post/modify/<int:id>',views.modify_post,name = 'modify_post'),
    path('post/<int:id>',views.post, name = 'post'),
    path('post/<int:post_id>/comments',views.get_post_comments, name = 'post'),
    path('comment/<int:id>',views.comment, name = 'comment_action'),
    path('posts/<int:id>',views.post_page, name = 'post_page'),
    path('post/favorite/<int:id>',views.favorite, name = "favorite"),

    
    path('post/react/<int:post_id>',views.react_post,name="react"),
    path('post/comment/new/<int:post_id>',views.create_comment, name="comment"),
    path('comment/react/<int:comment_id>',views.react_comment,name="react_comment"),

    path('contents/<int:id>',views.content_post_page, name = 'content_post_page'),
    path('contents/<int:content_id>/comments',views.get_content_comments, name = 'content_comments'),
    path('contents/<int:content_id>/comments/add',views.add_content_comment, name = 'content_comments'),
    path('contents/react/<int:content_id>',views.react_to_content, name='react_to_content'),
    
    path('notifications', views.notifications, name='notifications'),
    path('notifications/all',views.get_notifications, name='all_notifications'),
    path('notifications/mark_as_read/all',views.mark_all_notifs_as_read, name='mark_notifications_as_read'),
    path('notifications/mark_as_read/<int:notification_id>',views.mark_notif_as_read, name='mark_notification_as_read'),
    path('battle points',views.battle_points, name="battle_points"),

    path('rankings', views.rankings, name = 'rankings'),


    #EZOIC
    path('ezoic-3jZENPJ2HyQHll4Ye2ZCBVIua866XL.html', views.ezoic_file, name = 'ezoic_file'),

]