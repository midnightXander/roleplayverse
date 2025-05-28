from django.db import models
from users.models import *


class MontizationMetrics(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    earnings =  models.DecimalField(default=0, max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.player.user}"