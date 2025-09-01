from django.db import models
from users.models import *
import core.models as core_models
import random

def generate_login_code():
    numerical_part = str(random.randint(1000, 9999))
    alphabetical_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=4))
    return numerical_part + alphabetical_part



class MontizationMetrics(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    earnings =  models.DecimalField(default=0, max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user}"

class Payment(models.Model):
    # type = models.CharField(max_length=20, choices=[
    #     ('mobile_money', 'Mobile Money'),
    #     ('paypal', 'PayPal'),
    #     ('stripe', 'Stripe'),
    #     ('crypto', 'Crypto')
    # ], default = 'mobile_money')
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    motif = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=100, unique=True, default=core_models.generate_custom_id)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed')
    ], default='pending')
    def __str__(self):
        return f"{self.player.user}"

class PaymentRequest(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    adress = models.CharField(max_length=100)
    method = models.CharField(max_length=20, choices=[
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('crypto', 'Crypto')
    ], default = 'paypal')
    details = models.TextField(help_text="Provide necessary details like email for PayPal, wallet address for crypto, etc.")
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('rejected', 'Rejected')
    ], default='pending')
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user} - {self.amount} via {self.method} - {self.status}"    


class Creator(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='creators')
    login_code = models.CharField(max_length=100, unique=True, default=generate_login_code)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user}"

class CreatorLink(models.Model):
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE)
    link = models.URLField()
    platform = models.CharField(max_length=50, choices=[
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('twitch', 'Twitch'),
        ('patreon', 'Patreon'),
        ('other', 'Other')
    ], default='other')
    date_created = models.DateTimeField(auto_now_add=True)
    data = models.JSONField(null=True, blank=True)
    def __str__(self):
        return f"{self.creator.player.user} - {self.platform}"
    