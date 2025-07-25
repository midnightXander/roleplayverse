from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from api.utility import send_push_notification
from moderator.models import Moderator
from users.users_utility import get_player
from .models import *
from pathlib import Path
import os
import json
from django.utils import timezone
from dotenv import load_dotenv
from core.emails import send_email
import random

BASE_DIR = Path(__file__).resolve().parent.parent

def product_data(product:Product):
    return {
        'id': product.id,
        'title': product.title,
        'slug': product.slug,
        'description': product.description,
        'short_description': product.short_description,
        'type': product.type,
        'price': str(product.price),
        'available_stock': product.available_stock,
        'is_active': product.is_active,
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'images': [image.image.url for image in ProductImage.objects.filter(product = product)],
        'cover' : random.choice([image.image.url for image in ProductImage.objects.filter(product = product)])
    }

def product(request, product_id):
    # This is a placeholder for the product view logic
    # You can fetch the product details from the database using the product_id
    # and render them in a template.
    
    player = get_player(request.user)
    
    # Example:
    product = Product.objects.get(id=product_id)
    product.views += 1
    product.save()
    product_images = ProductImage.objects.filter(product = product)   
    product = product_data(product)

    # if request.user.is_authenticated:
    #     try:
    #         player = Player.objects.get(user = request.user)
    #     except Player.DoesNotExist:
    #         player = None
    # else: player = None        
    
    context = {'product': product, 'product_images': product_images}
    if player:
        context['player'] = player

    
    return render(request, 'store/product.html', context)  # Placeholder response

def checkout(request, product_id):
    player = get_player(request.user)
    countries_file = os.path.join(BASE_DIR, 'countries.json')
    with open(countries_file, 'r') as file:
        countries = json.load(file)
    # Example:
    product = Product.objects.get(id=product_id)
      
    

    if request.method == 'POST':
        # Handle the checkout process here
        # For example, create an order, process payment, etc.
        # This is a placeholder for the checkout logic
        first_name = request.POST.get('firstName')
        last_name = request.POST.get('lastName')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        state = request.POST.get('state')
        country = request.POST.get('country')
        city = request.POST.get('city')
        paymentMethod = request.POST.get('paymentMethod')
        quantity = request.POST.get('quantity', 1)
        
       
        new_order = Order.objects.create(
            total_amount=product.price * int(quantity),
            payment_method=paymentMethod,
            is_paid=False,  # Set to True if payment is successful
        )
        new_order_item  = OrderItem.objects.create(
            order = new_order,
            product=product,
            quantity=quantity,
            price=product.price
        )
        
        new_adress = OrderAdress.objects.create(
            order = new_order,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone,
            address_line1='',
            address_line2='',
            city=city,
            state=state,
            postal_code='',
            country=country,
            email = email,
        )

        if request.user.is_authenticated:
            new_order.user = request.user

        new_adress.save()
        new_order_item.save()
        new_order.save()

        #send a notification to a moderator 
        moderator = Moderator.objects.filter().first()
        # send_push_notification(
        #     moderator.user, 
        #     f"Nouvelle commande de {request.user.username}", 
        #     f"Un nouveau client a passé une commande pour {product.title}."
        # ) 
        order_username = request.user.username if request.user.is_authenticated else "Anonyme"
        send_email(
            title = "Nouvelle commande",
            subject=f"Nouvelle commande de {order_username}",
            body=f"Un nouveau client a passé une commande pour {product.title}.",
            recipient_email = moderator.user.email) 

        return HttpResponseRedirect("/store/checkout/success")  # Redirect to a success page or order confirmation page

    product.views += 1
    product.save()
    product = product_data(product) 
    context = {'product': product, 'countries':countries}
    if player:
        context['player'] = player


    return render(request, 'store/checkout.html', context) 

def checkout_success(request):
    player = get_player(request.user)
    context = {}
    if player:
        context['player'] = player
    return render(request, 'store/checkout_success.html', context)