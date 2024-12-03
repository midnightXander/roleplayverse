from django.contrib import admin
from .models import *

admin.site.register(Tournament)
admin.site.register(TournamentRequest)
admin.site.register(TournamentRefreeRequest)
admin.site.register(FighterTournament)
admin.site.register(RefreeTournament)

