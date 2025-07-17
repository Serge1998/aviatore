import pygame
import random
import time

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
WIDTH, HEIGHT = 1200, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aviator Game")

# Zone de jeu délimitée
GAME_AREA_X = 250
GAME_AREA_Y = 100
GAME_AREA_WIDTH = 900
GAME_AREA_HEIGHT = 400
game_area = pygame.Rect(GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT)

# Couleurs
WHITE = (255, 255, 255)
BLACK = (25, 25, 25)
RED = (255, 0, 0)
GREEN = (0, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 255)
SKY_BLUE = (135, 206, 235)  # Fond bleu ciel
CURVE_COLOR = (255, 255, 0)  # Couleur de la courbe (jaune, personnalisable)

# Polices
font = pygame.font.SysFont("arial", 20)
small_font = pygame.font.SysFont("arial", 20)

# Charger les images
try:
    airplane_image = pygame.image.load("airplane.png")
    airplane_image = pygame.transform.scale(airplane_image, (50, 50))
except FileNotFoundError:
    airplane_image = None
try:
    crash_image = pygame.image.load("crash.png")
    crash_image = pygame.transform.scale(crash_image, (50, 50))
except FileNotFoundError:
    crash_image = None

# Bouton d’arrêt
stop_button_rect = pygame.Rect(WIDTH - 700, HEIGHT - 100, 110, 60)
stop_button_text = small_font.render("Arrêter", True, WHITE)

# Variables du jeu
bet_amount = 0  # Pas de mise par défaut
balance = 10000  # Solde initial en F CFA
initial_balance = 10000  # Solde pour réinitialisation
multiplier = 1.0
game_state = "betting"  # États : "betting", "flying", "crashed", "game_over"
crash_point = 0
cashout_multiplier = 2.0
next_crash_point = round(random.uniform(1, 20), 2)  # Crash initial pour le premier tour
history = []
multiplier_history = []
running = True
last_state_change = 0
delay_between_rounds = 7  # Délai entre tours
betting_delay = 5  # Délai pour placer une mise
airplane_pos = [GAME_AREA_X, GAME_AREA_Y + GAME_AREA_HEIGHT - 50]  # Position initiale de l'avion
bet_input_active = True  # Entrée active dans "betting"
bet_input_text = ""  # Champ vide
has_cashout = False  # Indique si le parieur a encaissé
cashout_value = 1  # Stocke le multiplicateur au moment de l’encaissement
last_input_time = 0  # Dernier moment de saisie
input_delay = 0.5  # Délai de 0,5 seconde pour valider la mise

# Fonction pour générer un multiplicateur cible
def generate_cashout_multiplier():
    return round(random.uniform(1, 20), 2)

# Boucle principale
clock = pygame.time.Clock()
start_time = 0

while running:
    screen.fill(BLACK)
    
    # Dessiner la zone de jeu délimitée avec fond bleu ciel
    screen.fill(SKY_BLUE, game_area)  # Fond bleu ciel
    pygame.draw.rect(screen, WHITE, game_area, 2)  # Bordure blanche de 2 pixels
    
    # Gestion des événements
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == "betting":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    bet_input_text = bet_input_text[:-1] if bet_input_text else ""
                    last_input_time = time.time()  # Mettre à jour le temps de saisie
                elif event.unicode.isdigit() or event.unicode == '.':
                    bet_input_text += event.unicode
                    last_input_time = time.time()  # Mettre à jour le temps de saisie
        elif game_state == "flying" and not has_cashout and bet_amount > 0:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stop_button_rect.collidepoint(event.pos):
                    # Encaisser manuellement
                    winnings = bet_amount * multiplier
                    balance += winnings
                    cashout_value = multiplier  # Stocker le multiplicateur d’encaissement
                    history.append(multiplier)
                    has_cashout = True
                    bet_amount = 0

    # Logique du jeu
    current_time = time.time()

    if game_state == "betting":
        # Réinitialiser le solde si nécessaire
        if balance <= 0:
            balance = initial_balance
            bet_input_text = ""
            bet_input_active = True
            last_input_time = current_time
        # Vérifier si la saisie est valide après un délai
        if bet_input_active and bet_input_text and current_time - last_input_time >= input_delay:
            try:
                new_bet = float(bet_input_text)
                if new_bet > 0 and new_bet <= balance:
                    bet_amount = new_bet
                    balance -= bet_amount  # Décrémenter le solde
                    bet_input_active = False
                    game_state = "flying"  # Lancer immédiatement
                    multiplier = 1.0
                    crash_point = next_crash_point  # Crash basé sur le tour précédent
                    cashout_multiplier = generate_cashout_multiplier()
                    next_crash_point = cashout_multiplier  # Préparer le crash du tour suivant
                    start_time = current_time
                    last_state_change = current_time
                    multiplier_history = [(current_time, 1.0)]
                    airplane_pos = [GAME_AREA_X, GAME_AREA_Y + GAME_AREA_HEIGHT - 50]
                    has_cashout = False
                    cashout_value = 0
                    bet_input_text = ""  # Réinitialiser le champ de saisie
            except ValueError:
                pass  # Ignorer les saisies invalides
        # Passer à "flying" après betting_delay si aucune saisie
        if current_time - last_state_change >= betting_delay and bet_input_active:
            game_state = "flying"
            multiplier = 1.0
            crash_point = next_crash_point  # Crash basé sur le tour précédent
            cashout_multiplier = generate_cashout_multiplier()
            next_crash_point = cashout_multiplier  # Préparer le crash du tour suivant
            start_time = current_time
            last_state_change = current_time
            multiplier_history = [(current_time, 1.0)]
            airplane_pos = [GAME_AREA_X, GAME_AREA_Y + GAME_AREA_HEIGHT - 50]
            has_cashout = False
            cashout_value = 0
            bet_input_active = False
            bet_input_text = ""

    elif game_state == "flying":
        # Augmenter le multiplicateur (fonction polynomiale)
        elapsed_time = current_time - start_time
        multiplier = round(0.05 * elapsed_time**2 + 0.3 * elapsed_time + 1.0, 2)
        multiplier_history.append((current_time, multiplier))
        
        # Mettre à jour la position de l'avion
        airplane_pos[0] = min(GAME_AREA_X + (elapsed_time * 50), GAME_AREA_X + GAME_AREA_WIDTH - 50)
        airplane_pos[1] = max(GAME_AREA_Y + 10, min(GAME_AREA_Y + GAME_AREA_HEIGHT - 50, GAME_AREA_Y + GAME_AREA_HEIGHT - (multiplier * 10)))
        
        # Crash
        if multiplier >= crash_point:
            history.append(multiplier)  # Enregistrer le multiplicateur du crash
            game_state = "crashed"
            last_state_change = current_time
    
    elif game_state == "crashed":
        # Passer au tour suivant après 7 secondes
        if current_time - last_state_change >= delay_between_rounds:
            game_state = "betting"
            bet_input_active = True
            bet_input_text = ""
            bet_amount = 0
            last_state_change = current_time
            last_input_time = current_time  # Réinitialiser pour la nouvelle phase de saisie
    
    elif game_state == "game_over":
        pass

    # Affichage
    # Historique des multiplicateurs
    history_text = f"Historique: {', '.join(f'{m:.2f}x' for m in history[-13:]) if history else 'Aucun'}"
    history_surface = small_font.render(history_text, True, WHITE)
    screen.blit(history_surface, (GAME_AREA_X, GAME_AREA_Y - 30))
    
    # Solde
    balance_text = font.render(f"Solde: {balance:.2f} F CFA", True, WHITE)
    screen.blit(balance_text, (10, 10))
    
    # Mise
    bet_text = font.render(f"Mise: {bet_amount:.2f} F CFA", True, WHITE)
    screen.blit(bet_text, (10, 50))
    if game_state == "betting":
        input_text = small_font.render(f" Mise ici: {bet_input_text}", True, YELLOW)
        screen.blit(input_text, (10, 80))
    elif game_state == "flying" and has_cashout and bet_amount == 0:
        status_text = small_font.render("Mise encaissée !", True, GREEN)
        screen.blit(status_text, (10, 80))
    elif game_state == "flying" and bet_amount == 0 and not has_cashout:
        status_text = small_font.render("", True, WHITE)
        screen.blit(status_text, (10, 80))
    
    # Multiplicateur et compteur de gain potentiel
    if game_state in ["flying", "crashed"]:
        multiplier_text = font.render(f" {multiplier:.2f}x", True, GREEN if game_state == "flying" else RED)
        screen.blit(multiplier_text, (WIDTH // 2 - 100, HEIGHT // 2))
        if game_state == "flying" and bet_amount > 0 and not has_cashout:
            potential_winnings = bet_amount * multiplier
            potential_text = small_font.render(f"Gain potentiel: {potential_winnings:.2f} F CFA", True, YELLOW)
            screen.blit(potential_text, (WIDTH // 2 - 100, HEIGHT // 2 + 30))
    
    # Courbe du multiplicateur
    if multiplier_history:
        points = []
        for i, (t, m) in enumerate(multiplier_history):
            x = GAME_AREA_X + min((t - start_time) * 50, GAME_AREA_WIDTH - 10)
            y = max(GAME_AREA_Y + 10, min(GAME_AREA_Y + GAME_AREA_HEIGHT - 10, GAME_AREA_Y + GAME_AREA_HEIGHT - (m * 10)))
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(screen, CURVE_COLOR, False, points, 2)
    
    # Statut
    if game_state == "betting":
        status_text = small_font.render(f" (départ dans {betting_delay - (current_time - last_state_change):.1f}s)...", True, WHITE)
        screen.blit(status_text, (10, HEIGHT - 50))
        # Afficher le crash point du tour actuel (basé sur le tour précédent)
        crash_text = small_font.render(f"Prochain crash: {next_crash_point:.2f}x", True, RED)
        screen.blit(crash_text, (10, HEIGHT - 80))
    elif game_state == "flying":
        status_text = small_font.render(f" (Cible: {cashout_multiplier:.2f}x, Crash: {crash_point:.2f}x, Prochain crash: {next_crash_point:.2f}x)", True, WHITE)
        screen.blit(status_text, (10, HEIGHT - 50))
        # Afficher le bouton d’arrêt si mise > 0 et pas encore encaissé
        if bet_amount > 0 and not has_cashout:
            pygame.draw.rect(screen, RED, stop_button_rect)
            screen.blit(stop_button_text, (stop_button_rect.x + 10, stop_button_rect.y + 10))
    elif game_state == "crashed":
        if has_cashout:
            status_text = small_font.render(f"Gains: {bet_amount * cashout_value:.2f} F CFA", True, GREEN)
            screen.blit(status_text, (10, HEIGHT - 80))
        elif bet_amount > 0:
            status_text = small_font.render("Perdu", True, RED)
            screen.blit(status_text, (10, HEIGHT - 80))
        screen.blit(small_font.render("Nouveau tour dans 7s...", True, WHITE), (10, HEIGHT - 50))
    
    # Afficher l'avion
    if game_state == "flying":
        if airplane_image:
            screen.blit(airplane_image, airplane_pos)
        else:
            pygame.draw.rect(screen, BLUE, (airplane_pos[0], airplane_pos[1], 50, 50))
    elif game_state == "crashed" and crash_image:
        screen.blit(crash_image, airplane_pos)
    
    pygame.display.flip()
    clock.tick(60)

# Fermer Pygame
pygame.quit()