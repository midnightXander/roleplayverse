from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('terms',views.terms, name = 'terms'),
]