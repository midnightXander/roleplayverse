from django.contrib import admin
from .models import *

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Reaction)
admin.site.register(Notification)
admin.site.register(SavedPost)
admin.site.register(Feed)
