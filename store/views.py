from django.shortcuts import render

from users.users_utility import get_player
from .models import *


def product_data(product:Product):
    return {
        'id': product.id,
        'title': product.title,
        'slug': product.slug,
        'description': product.description,
        'type': product.type,
        'price': str(product.price),
        'available_stock': product.available_stock,
        'is_active': product.is_active,
        'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        'images': [image.image.url for image in ProductImage.objects.filter(product = product)],
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
