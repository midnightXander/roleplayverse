app_name = 'api'
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/register/', views.CreateUserView.as_view(), name='register' ),
    path('token/', TokenObtainPairView.as_view(), name ='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name = 'refresh'),
    path('feed', views.Feed.as_view(), name= 'feed' ),
    path('posts', views.PostListCreate.as_view()),
    path('posts/<int:pk>', views.PostApi.as_view()),
    path('post/reactions/<int:post_id>', views.PostReactionListCreate.as_view()),
    path('post/<int:post_id>/comments', views.CommentListCreate.as_view()),
    path('comment/<int:id>', views.CommentApi.as_view()),
    path('comment/reactions/<int:comment_id>', views.CommentReactionListCreate.as_view()),
    path('notifications/all', views.NotificationLst.as_view()),
    
    #battles
    path('battles/textpads/<int:battle_id>',views.TextPadListCreate.as_view()),
    path('battles/textpads/react/<int:textpad_id>',views.TextpadReactionListCreate.as_view()),
    path('battles/textpads/<int:battle_id>/comments', views.TextPadCommentList.as_view()),
    path('battles/requests', views.BattleRequestsListCreate.as_view()),
    path('battles/accept/<int:request_id>', views.BattleAccept.as_view()),
    path('battles/battle_room/<int:battle_id>',views.BattleRoom.as_view()),

    path('player',views.CurrentPlayer.as_view()),
    

    path('save-subscription/', views.save_subscription, name='save_subscriptions'),
]
