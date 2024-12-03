from django.contrib import admin
from .models import *


admin.site.register(Battle)
admin.site.register(BattleRequest)
admin.site.register(BattleAcceptor)
admin.site.register(RefreeingProposal)
admin.site.register(TextPad)
admin.site.register(RefereeRating)
admin.site.register(Rule)
admin.site.register(RefreeTest)

