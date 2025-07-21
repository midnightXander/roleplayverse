app_name = 'api'
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('user/register/', views.CreateUserView.as_view(), name='register' ),
    path('token/', TokenObtainPairView.as_view(), name ='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name = 'refresh'),
    path('feed', views.Feed.as_view(), name= 'feed' ),
    path('post/<int:pk>', views.Post.as_view(), name='post'),
    path('save-subscription/', views.save_subscription, name='save_subscriptions'),
]
