"""
URL configuration for para project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    # path('admin/', admin.site.urls),
    path('adminxyz/', admin.site.urls),
    path('',include('core.urls',namespace='core')),
    path('users/',include('users.urls',namespace='users')),
    path('chats/',include('chat.urls',namespace='chats')),
    path('characters/',include('characters.urls',namespace='characters')),
    path('battles/',include('battles.urls',namespace='battles')),
    path('events/',include('events.urls',namespace='events')),
    path('blog/', include('blog.urls',namespace='blog')),
    path('moderator/', include('moderator.urls', namespace = 'moderator')),
    path('legal/', include('legal.urls', namespace = 'legal')),
    path('api/',include('api.urls',namespace='api')),
    path('monetization/',include('monetization.urls',namespace='monetization')),
    path('metrics/',include('metrics.urls',namespace='metrics')),
    path('adventure/',include('adventure.urls',namespace='adventure')),
    path('ai/',include('ai.urls',namespace='ai')),
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
    path('',include('pwa.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)