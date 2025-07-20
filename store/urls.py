from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('products/<int:product_id>', views.product, name='index'),
]
