from django.db import models
from django.contrib.auth.models import User
from users.models import Player
from django.utils.text import slugify
# class Category(models.Model):
#     name = models.CharField(max_length=100)
#     slug = models.SlugField(unique=True)
#     description = models.TextField(blank=True)
#     icon = models.ImageField(upload_to='category_icons/', blank=True)

#     def __str__(self):
#         return self.name



class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('physical', 'Produit physique'),
        ('digital', 'Produit numérique'),
        ('bundle', 'Pack RP + physique'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.TextField()
    description = models.TextField()
    #category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    #image = models.ImageField(upload_to='product_images/')
    type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default = 'physical')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    #price = models.PositiveIntegerField(null=True, blank=True)  
    available_stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title     
    
    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn't already exist
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class AffiliateProduct(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='affiliate_product_images/')
    link = models.URLField()
    clicks = models.PositiveIntegerField(default=0) 
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} : {self.clicks}"
    
    def save(self, *args, **kwargs):
        if not self.slug:  # Only generate slug if it doesn't already exist
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.title}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)  # ex: MTN MoMo, PayPal, RP Credits
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Commande {self.id} par {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

class OrderAdress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='address')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Adresse pour {self.first_name} {self.last_name}"