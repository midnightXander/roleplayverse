app_name = 'api'
from django.urls import path, include
from . import views
urlpatterns = [

    path('save-subscription/', views.save_subscription, name='save_subscriptions'),


]
