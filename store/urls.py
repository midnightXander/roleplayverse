from django.urls import path, include
from . import views

app_name = 'store'

urlpatterns = [
    path('products/<int:product_id>', views.product, name='product'),
    path('checkout/<int:product_id>', views.checkout, name='checkout'),
    path('checkout/success', views.checkout_success, name='checkout_success'),
]
