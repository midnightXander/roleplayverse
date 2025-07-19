from django.db import models
from users.models import *
import core.models as core_models

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
    