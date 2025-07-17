from django.contrib import admin

# Register your models here.
from .models import GameState, PlayerProfile, GameHistory

admin.site.register(GameState)
admin.site.register(PlayerProfile)
admin.site.register(GameHistory)
