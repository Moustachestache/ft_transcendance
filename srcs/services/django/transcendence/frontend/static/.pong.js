let keyEventType = 0;
// Game refresh img
let interval = null;
//IA
let firstTouchAfterPoint = false;
let isAi_p1 = false;
let isAi_p2 = false;

// Keyboard variable
let upPressed_p1 = false;
let downPressed_p1 = false;

let upPressed_p2 = false;
let downPressed_p2 = false;

// Paddle variable
let paddleWidth = 10;
let paddleHeight = 100;
let paddleSpeed = 0.8;

let posX_p1;
let posX_p2;

let posY_p1;
let posY_p2;



// Ball variable

let posX_ball;
let posY_ball;
let ballRadius = 10;
let ballSpeedX = 0.8;
let ballSpeedY = 1;

// Draw image
function drawImage(context) {
    const image = new Image();
    image.src = "/static/Avatar_world_map_opacity.jpg";
    context.imageSmoothingEnabled = false;
    context.drawImage(image , 0, 0, 765, 418);
}

// Draw ball
function drawBall(context) {
    context.beginPath();
    context.arc(posX_ball, posY_ball, ballRadius, 0, Math.PI * 2);
    context.fillStyle = "white";
    context.fill();
    context.closePath();
}

// Draw paddle
function drawPaddle(context, x, y) {
    context.fillStyle = "white";
    context.fillRect(x, y, paddleWidth, paddleHeight);
}

// Move ball
async function moveBall(canvas) {
    posX_ball += ballSpeedX;
    posY_ball += ballSpeedY;

    // Collisions avec les murs (haut et bas)
    if (posY_ball + ballRadius > canvas.height || posY_ball - ballRadius < 0) {
        ballSpeedY = -ballSpeedY;
    }

    // Le joueur qui perd le round, reçois la balle au prochain round
    // Collision mur Gauche
    if (posX_ball - ballRadius < 0) {
        resetBall(canvas, -0.8);
    }
    // Collision mur Droit
    if (posX_ball + ballRadius > canvas.width) {
        resetBall(canvas, 0.8);
    }

    // Collision avec les joueurs
    // p1
    if (posX_ball - ballRadius < posX_p1 + paddleWidth) {
        if (posY_ball > posY_p1 && posY_ball < posY_p1 + paddleHeight) {
            ballSpeedX = -ballSpeedX;
            if (ballSpeedX < 0) {
                ballSpeedX -= 0.1;
            }
            else {
                ballSpeedX += 0.1;
            }

            // Ou touche la balle ?
            let middlePaddle = posY_p1 + paddleHeight / 2;

            // en haut de la raquette ?
            if (posY_ball < middlePaddle - paddleHeight / 6) {
                ballSpeedY = Math.random() * -1;
            }
            // en bas de la raquette ?
            else if (posY_ball > middlePaddle + paddleHeight / 6) {
                ballSpeedY = Math.random(); // Déplacement vers le bas
            }
            // au centre de la raquette ?
            else {
            }
            if (firstTouchAfterPoint === false) {
                firstTouchAfterPoint = true;
            }
        }
    }
    // p2
    if (posX_ball + ballRadius > posX_p2) {
        if (posY_ball > posY_p2 && posY_ball < posY_p2 + paddleHeight) {
            ballSpeedX = -ballSpeedX;
            if (ballSpeedX < 0) {
                ballSpeedX -= 0.1;
            }
            else {
                ballSpeedX += 0.1;
            }
            // Ou touche la balle ?
            let middlePaddle = posY_p2 + paddleHeight / 2;

            // en haut de la raquette ?
            if (posY_ball < middlePaddle - paddleHeight / 6) {
                ballSpeedY = Math.random() * -1;
            }
            // Si la balle touche la partie inférieure de la raquette
            else if (posY_ball > middlePaddle + paddleHeight / 6) {
                ballSpeedY = Math.random();
            }
            // au centre de la raquette ?
            else {
            }
            if (firstTouchAfterPoint === false) {
                firstTouchAfterPoint = true;
            }
        }
    }
}

let lastMoveTime_p1 = Date.now();
let lastMoveTime_p2 = Date.now();
let nbr_move = 0;
// Move Paddle
async function movePaddle(canvas) {
    let reactionInterval = 40;
    // Mouvement :
    //p1
    if (isAi_p1 === true) {
        if ((Date.now() - lastMoveTime_p1 > reactionInterval) && (posX_ball > canvas.width / 3 && posX_ball < canvas.width)) {
            const targetY = posY_ball - paddleHeight / 2;
            const distance = targetY - posY_p1;

            if (firstTouchAfterPoint === false) {
                randomInterval = 1;
            }
            else {
                randomInterval = (Math.random() * (1.3 - 0.7) + 0.7);
            }
            if (distance > 0) {
                posY_p1 += paddleSpeed
            }
            else if (distance < 0) {
                posY_p1 -= paddleSpeed;
            }
        }
        lastMoveTime_p1 = Date.now();
    }
    else {
        // p1 Up
        if (upPressed_p1) {
            posY_p1 -= paddleSpeed;
        }
        // p1 Down
        if (downPressed_p1) {
            posY_p1 += paddleSpeed;
        }
    }
    //p2
    if (isAi_p2 === true) {
        if ((Date.now() - lastMoveTime_p1 > reactionInterval) &&  (posX_ball > canvas.width / (Math.random() * (3 - 1.5) + 1.5) && posX_ball < canvas.width)) {
            const targetY = posY_ball - paddleHeight / 2;
            const distance = targetY - posY_p2;

            if (firstTouchAfterPoint === false) {
                reactionInterval = 0;
            }
            else {
                reactionInterval = 40 + (Math.random() * (2 - 0.8) + 0.8);
            }
            if (distance > 0) {
                posY_p2 += paddleSpeed;
            }
            else if (distance < 0) {
                posY_p2 -= paddleSpeed;
            }
            if (nbr_move >= Math.random() * (60 - 20) + 20) {
                nbr_move = 0;
                await sleep(Math.random() * (1400 - 200) + 200);
            }
            //randomInterval = (Math.random() * (2 - 0.5) + 0.5);
            lastMoveTime_p2 = Date.now();
            nbr_move += 1;
        }
    }
    else {
        // p2 Up
        if (upPressed_p2) {
            posY_p2 -= paddleSpeed;
        }
        // p2 Down
        if (downPressed_p2) {
            posY_p2 += paddleSpeed;
        }
    }
    // Empêcher la raquette du p1 de sortir du canvas
    if (posY_p1 < 0) {
        posY_p1 = 0; // Limite supérieure
    } else if (posY_p1 + paddleHeight > canvas.height) {
        posY_p1 = canvas.height - paddleHeight; // Limite inférieure
    }

    // Empêcher la raquette du p2 de sortir du canvas
    if (posY_p2 < 0) {
        posY_p2 = 0;
    } else if (posY_p2 + paddleHeight > canvas.height) {
        posY_p2 = canvas.height - paddleHeight;
    }
}

// Keyboard listener
function keyUpListeners(e) {
    //p1
    if (e.key === "z" || e.key === "Z") {
        upPressed_p1 = true;
    }
    else if (e.key === "s" || e.key === "S") {
        downPressed_p1 = true;
    }
    //p2
    else if (e.key === '9' && e.location === KeyboardEvent.DOM_KEY_LOCATION_NUMPAD) {
        upPressed_p2 = true;
    }
    else if (e.key === '6' && e.location === KeyboardEvent.DOM_KEY_LOCATION_NUMPAD) {
        downPressed_p2 = true;
    }
}
function keyDownListeners(e) {
    //p1
    if (e.key === "z" || e.key === "Z") {
        upPressed_p1 = false;
    }
    else if (e.key === "s" || e.key === "S") {
        downPressed_p1 = false;
    }
    //p2
    else if (e.key === '9' && e.location === KeyboardEvent.DOM_KEY_LOCATION_NUMPAD) {
        upPressed_p2 = false;
    }
    else if (e.key === '6' && e.location === KeyboardEvent.DOM_KEY_LOCATION_NUMPAD) {
        downPressed_p2 = false;
    }
}

function wsKeyDownListeners(e, socket) {
    if (e.key === 's' || e.key === 'S') {
        downPressed_p1 = false;
    }
    if (e.key === 'z' || e.key === 'Z') {
        upPressed_p1 = false;
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms))
}
async function wsKeyUpListeners(e, socket) {
    if (e.key === 's' || e.key === 'S') {
        await socket.send(JSON.stringify({
            type: "move_paddle",
            status: "down",
        }));
        await sleep(26);
        downPressed_p1 = true;
    }
    if (e.key === 'z' || e.key === 'Z') {
        await socket.send(JSON.stringify({
            type: "move_paddle",
            status: "up",
        }));
        await sleep(26);
        upPressed_p1 = true;
    }
}

function addKeyboardListeners(type, socket) {
    // Écoute des événements clavier
    if (type === 1) {
        window.addEventListener("keydown", keyUpListeners);
        window.addEventListener("keyup", keyDownListeners);
        keyEventType = 1;
    }
    else if (type === 2) {
        window.addEventListener("keydown", (e) => wsKeyUpListeners(e, socket));
        window.addEventListener("keyup", (e) => wsKeyDownListeners(e, socket));
        keyEventType = 2;
    }

}

function removeKeyboardListener() {
    if(keyEventType === 1) {
        window.removeEventListener("keydown", keyDownListeners);
        window.removeEventListener("keyup", keyUpListeners);
    }
    else if (keyEventType === 2) {
        window.removeEventListener("keydown", wsKeyUpListeners);
        window.removeEventListener("keyup", wsKeyDownListeners);
    }
}

//  Reset ball
function resetBall(canvas, speedX_axis) {
    posX_ball = canvas.width / 2;
    posY_ball = canvas.height / 2;

    ballSpeedX = speedX_axis;
    ballSpeedY = (Math.random() * 3) - 1.5;
    firstTouchAfterPoint = false;
}
// Reset Paddle
function resetPaddle(canvas) {
    posY_p1 = (canvas.height - paddleHeight) / 2;
    posY_p2 = (canvas.height - paddleHeight) / 2;
}

// Game brain
function pongFunnyDraw(canvas, context) {
    // Nettoyer le canvas avant de dessiner
    context.clearRect(0, 0, canvas.width, canvas.height);

    isAi_p1 = true;
    isAi_p2 = true;

    moveBall(canvas);
    movePaddle(canvas);

    drawImage(context)
    drawBall(context);
    drawPaddle(context, posX_p1, posY_p1);
    drawPaddle(context, posX_p2, posY_p2);
}

function pongPvP(canvas, context) {
    context.clearRect(0, 0, canvas.width, canvas.height);

    isAi_p1 = false;
    isAi_p2 = false;

    moveBall(canvas);
    movePaddle(canvas);

    drawImage(context);
    drawBall(context);
    drawPaddle(context, posX_p1, posY_p1);
    drawPaddle(context, posX_p2, posY_p2);
}

function pongPvAi(canvas, context) {
    // Nettoyer le canvas avant de dessiner
    context.clearRect(0, 0, canvas.width, canvas.height);

    isAi_p1 = false;
    isAi_p2 = true;

    moveBall(canvas);
    movePaddle(canvas);

    drawImage(context);
    drawBall(context);
    drawPaddle(context, posX_p1, posY_p1);
    drawPaddle(context, posX_p2, posY_p2);
}

function startGame(gameMode) {
    stopGame();
    const canvas = document.getElementById('pongCanvas');
    const context = canvas.getContext('2d');

    posX_p1 = 12 * (canvas.width / 768)
    posX_p2 = canvas.width - (paddleWidth + 12 * (canvas.width / 768));
    posY_p1 = (canvas.height - paddleHeight) / 2;
    posY_p2 = (canvas.height - paddleHeight) / 2;
    posX_ball = canvas.width / 2;
    posY_ball = canvas.height / 2;

    resetPaddle(canvas);
    resetBall(canvas, -1);
    addKeyboardListeners(1, null);
    scoreBoard();
    interval = setInterval(() => gameMode(canvas, context), 1);
}

function startWebsocketGame(socket, data) {
    stopGame()
    isAi_p1 = false;
    isAi_p2 = false;
    // Création du canvas et du contexte pour dessiner le jeu
    const canvas = document.getElementById("pongCanvas");
    const context = canvas.getContext("2d");

    posX_p1 = data.pos_p1.posX
    posY_p1 = data.pos_p1.posY
    posX_p2 = data.pos_p2.posX
    posY_p2 = data.pos_p2.posY
    ballSpeedX =  data.ball_position.vx
    ballSpeedY = data.ball_position.vy
    posX_ball = data.ball_position.x
    posY_ball = data.ball_position.y

    addKeyboardListeners(2, socket);
    resetPaddle(canvas);
    resetBall(canvas, -1);
    scoreBoard();

    drawImage(context);
    interval = setInterval(() => updateGame(canvas, context), 1000 / 60); // 60 FPS
}

function updateGame(canvas, context) {
    context.clearRect(0, 0, canvas.width, canvas.height);

    drawBall(context);
    drawPaddle(context, posX_p1, posY_p1);
    drawPaddle(context, posX_p2, posY_p2);
}

function updateGameState(data) {
    posX_p1 = data.pos_p1.posX
    posY_p1 = data.pos_p1.posY
    posX_p2 = data.pos_p2.posX
    posY_p2 = data.pos_p2.posY
    ballSpeedX =  data.ball_position.vx
    ballSpeedY = data.ball_position.vy
    posX_ball = data.ball_position.x
    posY_ball = data.ball_position.y
}

function stopGame() {
    clearInterval(interval);
    //removeKeyboardListener();
}

//SCORE BOARD SECTION

async function getUserData() {
    try {
        const tmpUserData = await m.request({
            method: "GET",
            url: "/api/login",
            withCredentials: true,
        })
        tmpUserData.userData = JSON.parse(tmpUserData.userData);
        tmpUserData.userData = tmpUserData.userData[0];
        const user = {
            userName: tmpUserData.username,
            userLang: tmpUserData.userData.fields.language,
            userId: tmpUserData.userData.fields.user,
            userPic: "",
        };
        if (tmpUserData.userData.fields.profile_pic == "")
            user.userPic = "/static/profileDefault.png"
        else
            user.userPic = "/media/" + tmpUserData.userData.fields.profile_pic;
        return user;
    }
    catch (error) {
        console.log('ERROR: ', error);
        return null;
    }
}
async function scoreBoard() {
    const userData = await getUserData();
    if (userData === null) {
        console.log("ça a chié dans la colle là");
    }
    m.render(document.getElementById('p1Username'), userData.userName);
}

// RESPONSIVE SECTION

window.addEventListener('resize', function() {
    resizeCanvas();
});

function resizeElements() {
    const canvas = document.getElementById('pongCanvas');

    paddleHeight = (canvas.height / 400) * 100;
    paddleSpeed = (canvas.height / 400) * 2.5;
    paddleWidth = (canvas.height / 400) * 10;
    ballRadius = (canvas.height / 400) * 10;

    posY_p1 = (canvas.height - paddleHeight) / 2;
    posY_p2 = (canvas.height - paddleHeight) / 2;

    posX_p1 = 12 * (canvas.width / 768);
    posX_p2 = canvas.width - (paddleWidth + 12 * (canvas.width / 768));

    posX_ball = canvas.width / 2;
    posY_ball = canvas.height / 2;
    //vitesse de la balle a modifié
}

function resizeCanvas() {
    const canvas = document.getElementById('pongCanvas');
    const container = document.getElementById('pong');

    const containerWidth = container.offsetWidth;
    const containerHeight = container.offsetHeight;

    // Proportion du canvas
    const ratio = 765 / 418;

    let newWidth = containerWidth;
    let newHeight = containerHeight;

    // Nouvelle dimension
    if (newWidth / ratio <= newHeight) {
        newHeight = newWidth / ratio;
    } else {
        newWidth = newHeight * ratio;
    }

    // MAJ
    if (newWidth > 765) {
        canvas.width = 765;
    } else {
        canvas.width = newWidth;
    }
    if (newWidth > 418) {
        canvas.height = 418;
    } else {
        canvas.height = newHeight;
    }

    resizeElements();
}

