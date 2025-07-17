const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');
canvas.width = 1200;
canvas.height = 600;

// Charger les images
const airplaneImage = new Image();
airplaneImage.src = 'assets/airplane.png';
const crashImage = new Image();
crashImage.src = 'assets/crash.png';

// Variables du jeu
let balance = 10000;
let betAmount = 0;
let multiplier = 1.0;
let gameState = 'betting';
let crashPoint = Math.round((Math.random() * 9 + 1) * 100) / 100;
let cashoutMultiplier = 2.0;
let history = [];
let multiplierHistory = [];
let startTime = Date.now() / 1000;
let lastStateChange = startTime;
const delayBetweenRounds = 7;
const bettingDelay = 5;
let airplanePos = [100, 450];
let betInputActive = true;
let betInputText = '';
let hasCashout = false;
let cashoutValue = 1;
let lastInputTime = startTime;
const inputDelay = 0.5;
let nextCrashPoint = crashPoint;

// Constantes
const GAME_AREA_X = 100;
const GAME_AREA_Y = 50;
const GAME_AREA_WIDTH = 900;
const GAME_AREA_HEIGHT = 400;
const SKY_BLUE = '#87CEEB';
const WHITE = '#FFFFFF';
const RED = '#FF0000';
const GREEN = '#00FF00';
const BLUE = '#0000FF';
const YELLOW = '#FFFF00';
const CURVE_COLOR = '#FFFF00';

// Éléments DOM
const historyDiv = document.getElementById('history');
const balanceDiv = document.getElementById('balance');
const betDiv = document.getElementById('bet');
const betInput = document.getElementById('bet-input');
const multiplierDiv = document.getElementById('multiplier');
const stopButton = document.getElementById('stop-button');
const statusDiv = document.getElementById('status');
const crashPointDiv = document.getElementById('crash-point');

// Gestion des événements
betInput.addEventListener('keydown', (e) => {
    if (gameState === 'betting') {
        if (e.key === 'Backspace') {
            betInputText = betInputText.slice(0, -1);
            lastInputTime = Date.now() / 1000;
        } else if (/[\d.]/.test(e.key)) {
            betInputText += e.key;
            lastInputTime = Date.now() / 1000;
        }
        betInput.value = betInputText;
    }
});

stopButton.addEventListener('click', () => {
    if (gameState === 'flying' && !hasCashout && betAmount > 0) {
        const winnings = betAmount * multiplier;
        balance += winnings;
        cashoutValue = multiplier;
        history.push(multiplier);
        hasCashout = true;
        betAmount = 0;
    }
});

// Boucle principale
function gameLoop() {
    const currentTime = Date.now() / 1000;

    if (gameState === 'betting') {
        if (balance <= 0) {
            balance = 10000;
            betInputText = '';
            betInputActive = true;
            lastInputTime = currentTime;
        }
        if (betInputActive && betInputText && currentTime - lastInputTime >= inputDelay) {
            try {
                const newBet = parseFloat(betInputText);
                if (newBet > 0 && newBet <= balance) {
                    betAmount = newBet;
                    balance -= betAmount;
                    betInputActive = false;
                    gameState = 'flying';
                    multiplier = 1.0;
                    crashPoint = nextCrashPoint;
                    cashoutMultiplier = Math.round((Math.random() * 9 + 1) * 100) / 100;
                    nextCrashPoint = cashoutMultiplier;
                    startTime = currentTime;
                    lastStateChange = currentTime;
                    multiplierHistory = [[currentTime, 1.0]];
                    airplanePos = [GAME_AREA_X, GAME_AREA_Y + GAME_AREA_HEIGHT - 50];
                    hasCashout = false;
                    cashoutValue = 0;
                    betInputText = '';
                    betInput.value = '';
                }
            } catch (e) {
                // Ignorer les saisies invalides
            }
        }
        if (currentTime - lastStateChange >= bettingDelay && betInputActive) {
            gameState = 'flying';
            multiplier = 1.0;
            crashPoint = nextCrashPoint;
            cashoutMultiplier = Math.round((Math.random() * 9 + 1) * 100) / 100;
            nextCrashPoint = cashoutMultiplier;
            startTime = currentTime;
            lastStateChange = currentTime;
            multiplierHistory = [[currentTime, 1.0]];
            airplanePos = [GAME_AREA_X, GAME_AREA_Y + GAME_AREA_HEIGHT - 50];
            hasCashout = false;
            cashoutValue = 0;
            betInputActive = false;
            betInputText = '';
            betInput.value = '';
        }
    } else if (gameState === 'flying') {
        const elapsedTime = currentTime - startTime;
        multiplier = Math.round((0.05 * elapsedTime**2 + 0.3 * elapsedTime + 1.0) * 100) / 100;
        multiplierHistory.push([currentTime, multiplier]);
        airplanePos[0] = Math.min(GAME_AREA_X + (elapsedTime * 50), GAME_AREA_X + GAME_AREA_WIDTH - 50);
        airplanePos[1] = Math.max(GAME_AREA_Y + 10, Math.min(GAME_AREA_Y + GAME_AREA_HEIGHT - 50, GAME_AREA_Y + GAME_AREA_HEIGHT - (multiplier * 10)));
        if (multiplier >= crashPoint) {
            history.push(multiplier);
            gameState = 'crashed';
            lastStateChange = currentTime;
        }
    } else if (gameState === 'crashed') {
        if (currentTime - lastStateChange >= delayBetweenRounds) {
            gameState = 'betting';
            betInputActive = true;
            betInputText = '';
            betAmount = 0;
            lastStateChange = currentTime;
            lastInputTime = currentTime;
        }
    }

    // Affichage
    ctx.fillStyle = BLACK;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = SKY_BLUE;
    ctx.fillRect(GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT);
    ctx.strokeStyle = WHITE;
    ctx.lineWidth = 2;
    ctx.strokeRect(GAME_AREA_X, GAME_AREA_Y, GAME_AREA_WIDTH, GAME_AREA_HEIGHT);

    historyDiv.textContent = `Historique: ${history.length ? history.slice(-5).map(m => `${m.toFixed(2)}x`).join(', ') : 'Aucun'}`;
    balanceDiv.textContent = `Solde: ${balance.toFixed(2)} F CFA`;
    betDiv.textContent = `Mise: ${betAmount.toFixed(2)} F CFA`;
    if (gameState === 'betting') {
        betInput.style.display = 'block';
    } else {
        betInput.style.display = 'none';
    }
    if (gameState === 'flying' && hasCashout && betAmount === 0) {
        statusDiv.textContent = 'Mise encaissée !';
        statusDiv.style.color = GREEN;
    } else if (gameState === 'flying' && betAmount === 0 && !hasCashout) {
        statusDiv.textContent = '';
    }
    if (gameState === 'flying' || gameState === 'crashed') {
        multiplierDiv.textContent = `${multiplier.toFixed(2)}x`;
        multiplierDiv.style.color = gameState === 'flying' ? GREEN : RED;
        if (gameState === 'flying' && betAmount > 0 && !hasCashout) {
            const potentialWinnings = betAmount * multiplier;
            multiplierDiv.textContent += `\nGain potentiel: ${potentialWinnings.toFixed(2)} F CFA`;
        }
    } else {
        multiplierDiv.textContent = '';
    }
    if (gameState === 'betting') {
        statusDiv.textContent = `(départ dans ${(bettingDelay - (currentTime - lastStateChange)).toFixed(1)}s)...`;
        statusDiv.style.color = WHITE;
        crashPointDiv.textContent = `Prochain crash: ${nextCrashPoint.toFixed(2)}x`;
        crashPointDiv.style.color = RED;
    } else if (gameState === 'flying') {
        statusDiv.textContent = `(Cible: ${cashoutMultiplier.toFixed(2)}x, Crash: ${crashPoint.toFixed(2)}x, Prochain crash: ${nextCrashPoint.toFixed(2)}x)`;
        statusDiv.style.color = WHITE;
        crashPointDiv.textContent = '';
        if (betAmount > 0 && !hasCashout) {
            stopButton.style.display = 'block';
        } else {
            stopButton.style.display = 'none';
        }
    } else if (gameState === 'crashed') {
        if (hasCashout) {
            statusDiv.textContent = `Gains: ${(betAmount * cashoutValue).toFixed(2)} F CFA`;
            statusDiv.style.color = GREEN;
        } else if (betAmount > 0) {
            statusDiv.textContent = 'Perdu';
            statusDiv.style.color = RED;
        } else {
            statusDiv.textContent = '';
        }
        crashPointDiv.textContent = 'Nouveau tour dans 7s...';
        crashPointDiv.style.color = WHITE;
    }

    // Courbe du multiplicateur
    if (multiplierHistory.length > 1) {
        ctx.beginPath();
        ctx.strokeStyle = CURVE_COLOR;
        ctx.lineWidth = 2;
        ctx.moveTo(GAME_AREA_X + (multiplierHistory[0][0] - startTime) * 50, GAME_AREA_Y + GAME_AREA_HEIGHT - (multiplierHistory[0][1] * 10));
        for (const [t, m] of multiplierHistory) {
            const x = GAME_AREA_X + Math.min((t - startTime) * 50, GAME_AREA_WIDTH - 10);
            const y = Math.max(GAME_AREA_Y + 10, Math.min(GAME_AREA_Y + GAME_AREA_HEIGHT - 10, GAME_AREA_Y + GAME_AREA_HEIGHT - (m * 10)));
            ctx.lineTo(x, y);
        }
        ctx.stroke();
    }

    // Avion
    if (gameState === 'flying' && airplaneImage.complete) {
        ctx.drawImage(airplaneImage, airplanePos[0], airplanePos[1], 50, 50);
    } else if (gameState === 'flying') {
        ctx.fillStyle = BLUE;
        ctx.fillRect(airplanePos[0], airplanePos[1], 50, 50);
    } else if (gameState === 'crashed' && crashImage.complete) {
        ctx.drawImage(crashImage, airplanePos[0], airplanePos[1], 50, 50);
    } else if (gameState === 'crashed') {
        ctx.fillStyle = RED;
        ctx.fillRect(airplanePos[0], airplanePos[1], 50, 50);
    }

    requestAnimationFrame(gameLoop);
}

// Lancer la boucle de jeu
requestAnimationFrame(gameLoop);

betInput.addEventListener('input', (e) => {
    if (gameState === 'betting') {
        betInputText = e.target.value.replace(/[^0-9.]/g, '').replace(/(\..*?)\./g, '$1');
        lastInputTime = Date.now() / 1000;
        betInput.value = betInputText;
    }
});

function saveGameState() {
    fetch('/api/update-game-state/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ balance, history })
    }).then(response => response.json()).then(data => console.log(data));
}
// Appeler saveGameState() après chaque mise ou encaissement