from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import PlayerProfile, GameHistory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
import json

@login_required
def acceuil(request):
    profile, created = PlayerProfile.objects.get_or_create(
        user=request.user,
        defaults={'balance': 10000.0, 'initial_balance': 10000.0}
    )
    history = GameHistory.objects.filter(user=request.user).order_by('-timestamp')[:13]
    return render(request, 'app/acceuil.html', {
        'balance': profile.balance,
        'history': [h.multiplier for h in history]
    })

@login_required
def update_game_state(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        profile = PlayerProfile.objects.get(user=request.user)
        
        bet_amount = data.get('bet_amount', 0)
        multiplier = data.get('multiplier', 0)
        winnings = data.get('winnings', 0)
        
        if bet_amount > 0 and bet_amount <= profile.balance:
            profile.balance -= bet_amount
            profile.save()
            GameHistory.objects.create(
                user=request.user,
                multiplier=multiplier,
                bet_amount=bet_amount,
                winnings=winnings
            )
        elif winnings > 0:
            profile.balance += winnings
            profile.save()
            GameHistory.objects.create(
                user=request.user,
                multiplier=multiplier,
                bet_amount=0,
                winnings=winnings
            )
        
        return JsonResponse({'balance': profile.balance})
    return JsonResponse({'error': 'Méthode non autorisée'}, status=400)

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('acceuil')
    else:
        form = UserCreationForm()
    return render(request, 'app/register.html', {'form': form})