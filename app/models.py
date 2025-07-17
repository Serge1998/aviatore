from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import User

class GameState(models.Model):
    field_name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    balance = models.FloatField(default=10000)
    history = models.JSONField(default=list)  # Stocke l'historique des multiplicateurs
    created_at = models.DateTimeField(auto_now_add=True)
    state_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"GameState {self.id}"
    

class PlayerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.FloatField(default=10000.0)  # Solde initial de 10 000 F CFA
    initial_balance = models.FloatField(default=10000.0)

    def __str__(self):
        return f"Profil de {self.user.username}"

class GameHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    multiplier = models.FloatField()  # Multiplicateur au moment du crash ou de l'encaissement
    bet_amount = models.FloatField()  # Montant parié
    winnings = models.FloatField(default=0.0)  # Gains (0 si perdu)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.multiplier}x - {self.timestamp}"