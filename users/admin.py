from django.contrib import admin
from users.models import *

admin.site.register(Family)
admin.site.register(Player)
admin.site.register(PlayerNotification)
admin.site.register(PlayerStat)
admin.site.register(RefreeStat)
admin.site.register(Badge)
admin.site.register(PlayerBadge)
admin.site.register(Achievement)
admin.site.register(PasswordRecoveryCode)

