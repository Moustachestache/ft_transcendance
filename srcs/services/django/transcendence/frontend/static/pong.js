/* 
pong game functions
 */
const matchmaking = new Matchmaking("/ws/matchmaking/");

const tournament = new Tournament("/ws/tournament/");

const match = new Match("/ws/match/");

const gameInfo = {}

const interpolation = {
    ball: { 
        from: { 
            x: 0, 
            y: 0 }, 
        to: { 
            x: 0,
            y: 0 }, 
        t: 1 },
    player1: { 
        from: 0, to: 0, t: 1 },
    player2: { 
        from: 0, to: 0, t: 1 },
};

window.onresize = () => {
    if (!gameInfo.pongCanvasGame)
        return ;
    setGameSizes();

    // flush game, redraw game -- note: i dont think we need this?
    if (gameInfo.isRunning == 1)
        drawGame();

    //  update elements
    gameInfo.ball.resize();
    gameInfo.player.resize();
    gameInfo.dummy.resize();

    //  re-display
    displayMessage();
    tournamentLoading();
};

function setGameSizes()
{
    //  get current sizes
    //  canvasWrapperElement
    gameInfo.canvasWidth = gameInfo.canvasWrapperElement.offsetWidth;

    // keeps 16/9 ratio to calculate height
    gameInfo.pongCanvasGame.height = gameInfo.canvasWidth * 0.5625;
    gameInfo.pongCanvasGame.width = gameInfo.canvasWidth;

    //  get ratio server vs local
    //  use to rescale
    //  both should be the same but you never know how weirdly we mite resize?
    gameInfo.pongCanvasGame.xRatio = gameInfo.pongCanvasGame.width / 1280;
    gameInfo.pongCanvasGame.yRatio = gameInfo.pongCanvasGame.height / 720;

    // font
    gameInfo.defaultFont = "ProtestRevolution"
    gameInfo.canvasFont = "";

    //  font relative to height
    gameInfo.pongCanvasGameContext.font = "" + gameInfo.pongCanvasGame.height / 6 + "px ProtestRevolution";
}

//  frontend
//  pong game functions
function    _initPong()
{
    // init variables
    // note: if we initialise in the document it 
    // doesnt work because the window isnt loaded
    gameInfo.isRunning = 1;

    //  create layers
    gameInfo.canvasWrapperElement = document.getElementById("gameCanvasWrapper");
    
    gameInfo.pongCanvasGame = document.getElementById("pongCanvasGame");
    gameInfo.pongCanvasGameContext = gameInfo.pongCanvasGame.getContext("2d");

    //  basic colour
    gameInfo.pongCanvasGameContext.fillStyle = "white";

    resetInterface();

    // calculate sizes
    setGameSizes();

    // player elements
    gameInfo.player = new Player('w', 's');
    gameInfo.player._init();


    gameInfo.dummy = new Paddle('o', 'l', -1); // -1 = dummy paddle, has no event initialised
    gameInfo.dummy._init();

    // ball
    gameInfo.ball = new Ball();
    gameInfo.ball._init();

    // message
    gameInfo.message = {}
    gameInfo.message.text = "";
    gameInfo.message.status = 0;

    // images
    gameInfo.image = {};
    gameInfo.image.hourglass = new Image();
    gameInfo.image.hourglass.src = "/static/hourglass-split.svg";
    gameInfo.image.person = new Image();
    gameInfo.image.person.src = "/static/person.svg"
    gameInfo.image.personCheck = new Image();
    gameInfo.image.personCheck.src = "static/person-check-fill.svg"
    /* var img = new Image(); */

    // tournament structure
    gameInfo.tournament = {};
    gameInfo.tournament.connected = 0;
    gameInfo.tournament.maxplayer = 4;
    gameInfo.tournament.remainingTime = 30;
    gameInfo.tournament.isLoading = 0;

    // adapt to display
    gameInfo.ball.resize();
    gameInfo.player.resize();
    gameInfo.dummy.resize();
}

function resetGame()
{
    gameInfo.isRunning = 1;

    resetInterface();
    clearMessage()

    gameInfo.ball.resize();
    gameInfo.player.resize();
    gameInfo.dummy.resize();
}

function pongHandler(jsonData)
{
    data = JSON.parse(jsonData);
    switch (data.signal)
    {
        case "msg":
            newMessage(data.msg);
            break;

        case "scoreData":
            gameInfo.score.player1 = data.player1;
            gameInfo.score.player2 = data.player2;
            drawPoints()
            break;

        case "gameEnd":
            //stopPong(data.msg)
            gameEnd(data.msg)
            break;

        case "connected":
            drawGame();
            resetGame()
            break;
    
        case "matchData":
            clearMessage();
            interpolation.player1.from = gameInfo.player._paddle._ypos;
            interpolation.player2.from = gameInfo.dummy._ypos;
            interpolation.ball.from.x = gameInfo.ball.xpos;
            interpolation.ball.from.y = gameInfo.ball.ypos;
        
            interpolation.player1.to = data.player1.y;
            interpolation.player2.to = data.player2.y;
            interpolation.ball.to.x = data.ball.x * gameInfo.pongCanvasGame.xRatio;
            interpolation.ball.to.y = data.ball.y * gameInfo.pongCanvasGame.xRatio;
        
            interpolation.player1.t = 0;
            interpolation.player2.t = 0;
            interpolation.ball.t = 0;
        
            gameInfo.time = data.time;
            break;
    }
}

/* 
[Tournament] Message from server: 
{"type": "send.data", 
"signal": "connected_players", 
"nbLoggedPlayers": "2", 
"nbMaxPlayers": "4", 
"remainingTime": "5"}
 */
function pongTournamentHandler(jsonData)
{
    flushCanvas();
    try {
        switch (jsonData.signal) {
            case "msg":
                newMessage(jsonData.msg)
                displayMessage()
                break;

            case "waiting_final":
                break;
        
            // loading screen
            case "connected_players":
                updateTournamentData(jsonData)
                tournamentLoading();
                break;

            case "disconnect":
                break;  
        }
    } catch (error) {
        console.log("error: exception in tournament socket: " + error);
    }
}

/* 
[Tournament] Message from server: 
{"type": "send.data", 
"signal": "connected_players", 
"nbLoggedPlayers": "2", 
"nbMaxPlayers": "4", 
"remainingTime": "5"}
*/

function updateTournamentData(jsonData)
{

    gameInfo.tournament.isLoading = 1;
    gameInfo.tournament.connected = jsonData.nbLoggedPlayers;
    gameInfo.tournament.maxplayer = jsonData.nbMaxPlayers;
    gameInfo.tournament.remainingTime = jsonData.remainingTime;
}

function tournamentLoading()
{

    if (gameInfo.tournament.isLoading == 0)
        return;

    let info = gameInfo.tournament;
    let ctx = gameInfo.pongCanvasGameContext;

    let ratio = gameInfo.pongCanvasGame.xRatio
    let w = gameInfo.pongCanvasGame.width
    let h = gameInfo.pongCanvasGame.height
    let imgSize = 100 * ratio;
    
    ctx.fillStyle = "white";
    gameInfo.pongCanvasGameContext.font = "" + (120 * ratio) + "px Arial";
    ctx.textAlign = "right";
    ctx.textBaseline = "top";

    // "waiting" line (hourglass, time)
    ctx.drawImage(gameInfo.image.hourglass, (w / 3), h / 3, imgSize, imgSize);
    ctx.fillText(gameInfo.tournament.remainingTime, (w / 3) * 2, h / 3)


    let ypos = (w / 4);
    let xpos = (h / 3) * 2;
    ctx.textAlign = "center";
    ctx.fillText(gameInfo.tournament.connected + "/" + gameInfo.tournament.maxplayer, ypos, xpos)
    for (let i = 0; i < gameInfo.tournament.maxplayer; i++)
    {
        ctx.globalAlpha = 1;
        if (i < gameInfo.tournament.connected)
            ctx.drawImage(gameInfo.image.personCheck, (ypos * 2) + (i * imgSize), xpos, imgSize, imgSize)
        else
        {
            ctx.globalAlpha = 0.5;
            ctx.drawImage(gameInfo.image.person, (ypos * 2) + (i * imgSize), xpos, imgSize, imgSize)  
        }
    }
    // ctx.globalAlpha = 0.4;
    ctx.globalAlpha = 1;
}

//  when tournament queue timeouts
function pongTournamentTimeout()
{
    flushCanvas();
    gameInfo.tournament.isLoading = 0;
}

//  add new message from receiving msg from socket
function newMessage(message)
{
    gameInfo.message.text = message;
    gameInfo.message.status = 1;
}

// if message, display it
function displayMessage()
{
    if (gameInfo.message.status == 1)
    {
        gameInfo.pongCanvasGameContext.textAlign = "center";
        gameInfo.pongCanvasGameContext.font = calculateFontSize(gameInfo.message.text)
        gameInfo.pongCanvasGameContext.fillText(gameInfo.message.text, gameInfo.pongCanvasGame.width / 2,  gameInfo.pongCanvasGame.height / 2);
    }
}

// flush message information
function clearMessage()
{
    gameInfo.message.status = 0;
}

function calculateInterpolation()
{
    const dt = 0.2;
    interpolation.player1.t = Math.min(interpolation.player1.t + dt, 1);
    interpolation.player2.t = Math.min(interpolation.player2.t + dt, 1);
    interpolation.ball.t = Math.min(interpolation.ball.t + dt, 1);

    gameInfo.player._paddle._ypos = linearInterpolation(interpolation.player1.from, interpolation.player1.to, interpolation.player1.t);
    gameInfo.dummy._ypos = linearInterpolation(interpolation.player2.from, interpolation.player2.to, interpolation.player2.t);
    gameInfo.ball.xpos = linearInterpolation(interpolation.ball.from.x, interpolation.ball.to.x, interpolation.ball.t);
    gameInfo.ball.ypos = linearInterpolation(interpolation.ball.from.y, interpolation.ball.to.y, interpolation.ball.t);
}

function linearInterpolation(a, b, t) {
    return a + (b - a) * t;
}

function calculateFontSize(message)
{
    // message.length
    var fontSize = gameInfo.pongCanvasGame.width / (message.length / 2);
    if (!fontSize)
        fontSize = gameInfo.pongCanvasGame.width / 5;
    return gameInfo.canvasFont = fontSize + "px " + gameInfo.defaultFont;
}

function updateTime()
{
    //  push new time
    document.getElementById('scoreboardTime').innerHTML = gameInfo.time;
}

function drawPoints()
{
    //  update points
    document.getElementById('scorePlayer1').innerHTML = gameInfo.score.player1;
    document.getElementById('scorePlayer2').innerHTML = gameInfo.score.player2;
}

function _initInterface(jsonData)
{
    if (jsonData.player_1.profile_pic)
        document.getElementById('imgPlayer1').src = "/media/" + jsonData.player_1.profile_pic + "?force";
    else
        document.getElementById('imgPlayer2').src = "/static/profileDefault.png";

    if (jsonData.player_2.profile_pic)
        document.getElementById('imgPlayer2').src = "/media/" + jsonData.player_2.profile_pic + "?force";
    else
        document.getElementById('imgPlayer2').src = "/static/profileDefault.png";
    
        

    document.getElementById('usernamePlayer1').innerHTML = jsonData.player_1.username;
    document.getElementById('usernamePlayer2').innerHTML = jsonData.player_2.username;
    
    // draw game interface
    showInterface()
}

function flushCanvas()
{
    gameInfo.pongCanvasGameContext.clearRect(0, 0, gameInfo.pongCanvasGame.width, gameInfo.pongCanvasGame.height);
}

function drawGame()
{
    if (gameInfo.isRunning == 0)
    {
        window.cancelAnimationFrame(drawGame);
        return ;
    }

    calculateInterpolation();

    // clear canvas
    flushCanvas()

    // redraw items
    gameInfo.player._paddle.redraw();
    gameInfo.dummy.redraw();
    gameInfo.ball.redraw();

    // time
    updateTime();
    displayMessage();
    tournamentLoading();

    window.requestAnimationFrame(drawGame);
}


//  entrypoint - executed from pageLoad -> pageSpecificTrigger
function    startPong()
{
    _initPong();
}

function hideInterface()
{
    //  hide interface
    document.getElementById("pongScoreboard").style.opacity = "0";
    document.getElementById("pongScoreboard").style.height = "0px";
}

function showInterface()
{
    document.getElementById("pongScoreboard").style.opacity = "1";
    document.getElementById("pongScoreboard").style.height = "100%";
    drawPoints()
}

function resetInterface()
{
    //  score info
    gameInfo.score = {}
    gameInfo.score.player1 = 0;
    gameInfo.score.player2 = 0;
    
    // time
    gameInfo.time = "0:00"
}

// launches once at the end of the game
// sets game.isRunning to 0
function gameEnd(message)
{

    gameInfo.isRunning = 0
    hideInterface();
    resetInterface();
    flushCanvas();
    newMessage(message);
    displayMessage();
}

function    stopPong(message)
{
    gameInfo.isRunning = 0

    match.disconnect();
    matchmaking.disconnect();
    tournament.disconnect();

    //  delete info
    gameInfo.player._destroy();
    gameInfo.dummy._destroy();


    gameInfo.pongCanvasGame = 0;

}

let playButtonState = 0;
let tournamentButtonState = 0;

function pageButtonFreeplay()
{
    startMatchmaking();
}


function pageButtonTournament()
{
    if (tournamentButtonState == 0)
    {
        document.getElementById("tournament_wrapper").style.height = "100%"
        document.getElementById("tournament_wrapper").style.opacity = "1"
        tournamentButtonState = 1.0;

    }
    else
    {
        document.getElementById("tournament_wrapper").style.height = "0px"
        document.getElementById("tournament_wrapper").style.opacity = "0"
        tournamentButtonState = 0;
    }
}
