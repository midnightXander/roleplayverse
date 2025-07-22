app_name = 'api'
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/register/', views.CreateUserView.as_view(), name='register' ),
    path('token/', TokenObtainPairView.as_view(), name ='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name = 'refresh'),
    path('feed', views.Feed.as_view(), name= 'feed' ),
    path('post/<int:pk>', views.PostApi.as_view()),
    path('posts', views.PostListCreate.as_view()),
    path('post/<int:post_id>/comments', views.CommentListCreate.as_view()),
    path('comment/<int:id>', views.CommentApi.as_view()),
    path('notifications/all', views.NotificationLst.as_view()),
    path('battles/textpads/<int:battle_id>',views.TextPadListCreate.as_view()),
    path('battles/textpads/<int:battle_id>/comments', views.TextPadCommentList.as_view()),
    path('battles/requests', views.BattleRequestsList.as_view()),
    path('save-subscription/', views.save_subscription, name='save_subscriptions'),
]
