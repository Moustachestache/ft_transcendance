let tmp_socket = null;

const connectToMatchmaking = (Mode) => {
    if (Mode === 'close_connection' && tmp_socket != null) {
        tmp_socket.send(JSON.stringify({
            type: "leave",
        }));
        tmp_socket.close();
        tmp_socket = null;
        button_management('no', 'remove');
        return ;
    }
    const socket = new WebSocket(`ws://localhost:8000/ws/matchmaking/`);
    tmp_socket = socket;

    socket.onopen = () => {
        console.log("Matchmaking connection opened");
        socket.send(JSON.stringify({
            type: "join",
            mode: Mode,
        }));
        button_management('no', 'yes');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "match_found") {
            socket.close();
            close_popup();
            connectToWebsocket(data.mode, data.match_id);
        }

    }
    socket.onclose = () => {
        console.log("Matchmaking connection closed.");
        tmp_socket = null;
    };
}


const connectToWebsocket = (mode, room_id) => {
    const socket = new WebSocket(`ws://localhost:8000/ws/pong/${room_id}/`);

    socket.onopen = () => {
        console.log("WebSocket connection opened.");
        socket.send(JSON.stringify({
            type: "none",
            message: "Player joined the match!",
        }));
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'startGame') {
                startWebsocketGame(socket, data);
        }
        if (data.type === 'update') {
                updateGameState(data);
        }
        if (data.type === 'game_over') {
            socket.close();
            startGame(pongFunnyDraw);
            if(data.tournament != null) {
               loadPage("play", "", true);
            }
        }
    };

    socket.onclose = () => {
        console.log("WebSocket connection closed.");
        button_management('yes', 'remove');
        button_management('no', 'remove');
    };
};

function open_popup_tournament() {
    document.getElementById('popup_tournament').style.display = 'flex';
}

function close_popup_tournament() {
    document.getElementById('popup_tournament').style.display = 'none';
}

function open_popup() {
    document.getElementById('popup').style.display = 'flex';
}

function close_popup() {
    document.getElementById('popup').style.display = 'none';
}


function handle_nav_tournament(event) {
    startTournamentMatchmaking('close_connection', null);
}

function handle_nav_matchmaking(event) {
    connectToMatchmaking('close_connection');
}

function handle_nav_ft_transcendance_button_matchmaking(event) {
    connectToMatchmaking('close_connection');
}

function handle_nav_ft_transcendance_button_tournament(event) {
    startTournamentMatchmaking('close_connection', null);
}

function handle_refresh_tournament() {
    startTournamentMatchmaking('close_connection', null);
}

function handle_refresh_matchmaking() {
    connectToMatchmaking('close_connection');
}

function button_management(is_tournament, add_event) {
    //nav_button 
    const ft_transcendance_button = document.querySelector("[href='/']")
    const nav_buttons = document.querySelectorAll('a.btn');
    const play_buttons = document.querySelectorAll('button');
    if (add_event === 'yes') {
        if (is_tournament === 'yes') {
            window.addEventListener('beforeunload', handle_refresh_tournament);
            ft_transcendance_button.addEventListener('click', handle_nav_ft_transcendance_button_tournament);
            for (let i = 0; i < nav_buttons.length; i++) {
                if (nav_buttons[i].getElementById("play") === "play") {
                    continue ;
                }
                nav_buttons[i].addEventListener('click', handle_nav_tournament);
            }
            for (let i = 0; i < play_buttons.length; i++) {
                if (play_buttons[i].id === "annuler_recherche_tournament" || play_buttons[i].id === "annuler_recherche") {
                    continue ;
                }
                play_buttons[i].disabled = true;
            }
        } 
        else {
            window.addEventListener('beforeunload', handle_refresh_matchmaking);
            ft_transcendance_button.addEventListener('click', handle_nav_ft_transcendance_button_matchmaking);
            for (let i = 0; i < nav_buttons.length; i++) {
                if (nav_buttons[i].getAttribute("href") === "play") {
                    continue ;
                }
                nav_buttons[i].addEventListener('click', handle_nav_matchmaking);
            }
            for (let i = 0; i < play_buttons.length; i++) {
                if (play_buttons[i].id === "annuler_recherche_tournament" || play_buttons[i].id === "annuler_recherche") {
                    continue ;
                }
                play_buttons[i].disabled = true;
            }
        }
      }
    else {
        if (is_tournament === 'yes') {
            window.removeEventListener('beforeunload', handle_refresh_tournament);
            ft_transcendance_button.removeEventListener('click', handle_nav_ft_transcendance_button_tournament);
            for (let i = 0; i < nav_buttons.length; i++) {
                if (nav_buttons[i].getAttribute("href") === "play") {
                    continue ;
                }
                nav_buttons[i].removeEventListener('click', handle_nav_tournament);
            }
            for (let i = 0; i < play_buttons.length; i++) {
                if (play_buttons[i].id === "annuler_recherche_tournament" || play_buttons[i].id === "annuler_recherche") {
                    continue ;
                }
                play_buttons[i].disabled = false;
            }
        } 
        else {
            window.removeEventListener('beforeunload', handle_refresh_matchmaking);
            ft_transcendance_button.removeEventListener('click', handle_nav_ft_transcendance_button_matchmaking);
            for (let i = 0; i < nav_buttons.length; i++) {
                if (nav_buttons[i].getAttribute("href") === "play") {
                    continue ;
                }
                nav_buttons[i].removeEventListener('click', handle_nav_matchmaking);
            }
            for (let i = 0; i < play_buttons.length; i++) {
                if (play_buttons[i].id === "annuler_recherche_tournament" || play_buttons[i].id === "annuler_recherche") {
                    continue ;
                }
                play_buttons[i].disabled = false;
            }
        }
    }
}


tmp_socket_tournament = null;

const startTournamentMatchmaking = (is_closed, button) => {
    if (is_closed === 'close_connection' && tmp_socket_tournament != null) {
        tmp_socket_tournament.send(JSON.stringify({
            type: "leave",
        }));
        tmp_socket_tournament.close();
        tmp_socket_tournament = null;
        button_management('yes', 'remove');
        return ;
    }
    //tmp_title = button.dataset.tournament;
    const tournament_title = button.dataset.tournament;
    const opponent = button.dataset.opponent;

    console.log("Tournoi:", tournament_title);
    console.log("Adversaire:", opponent);

    const socket = new WebSocket(`ws://localhost:8000/ws/tournament/${tournament_title}/`);
    tmp_socket_tournament = socket;

    socket.onopen = () => {
        console.log("Tournament connection opened.");
        socket.send(JSON.stringify({
            type:"create_match",
            opponent: opponent
        }));
        button_management('yes', 'yes');
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'match_found') {
            socket.close();
            connectToWebsocket(data.mode, data.room_id);
            close_popup_tournament();
        }
    };

    socket.onclose = () => {
        console.log("Tournament connection closed.");
    };
}