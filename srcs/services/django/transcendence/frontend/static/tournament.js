
class Tournament
{
    constructor(routing)
    {
        this.routing = routing;
        this.socket = null;
    }

    connect(tournamentId)
    {
        if (this.socket && this.socket.readyState === WebSocket.OPEN)
        {
            console.log("The client is already connected to the Tournament.");
            return ;
        }

        if (this.socket && this.socket.readyState !== WebSocket.CLOSED)
            this.socket.close();

        if (isNaN(tournamentId))
        {
            console.log("Error tournament Id is NaN.");
            return ;
        }

        this.tournamentId = tournamentId;

        this.socket = new WebSocket("wss://" + window.location.host + this.routing + tournamentId + "/");

        this.socket.onopen = () => {
            console.log("Connected to tournament:" + this.tournamentId + ".");
            this.connected = true;
        };

        this.socket.onmessage = (event) => {
            let obj = JSON.parse(event.data);
            pongTournamentHandler(obj);
            if (!obj.signal)
            {
                console.log("Error no signal in the received msg.")
                this.disconnect();
                return ;
            }
            if (obj.signal == 'match' && obj.match_id)
            {
                startPong();
                drawGame();
                match.connect(obj.match_id, obj);
            }
        };

        this.socket.onclose = () => {
            this.socket = null;
            pongTournamentTimeout();
            console.log('[Tournement] The server has closed the connection.')
        };

		this.socket.onerror = () => {
			this.disconnect();
		}
    }

    disconnect()
    {
        if (this.socket && this.socket.readyState === this.socket.OPEN)
        {
            this.socket.close();
            this.socket = null;
        }
        else
            console.log("Connection is already closed.");
    }

    send(data)
    {
        if (this.socket && this.socket.readyState === this.socket.OPEN)
        {
            this.socket.send(data);
            console.log("Data sent:", data);
        }
        else
            console.log("Send error, the socket is closed.");
    }

}

function startTournament(tournamentId)
{
    tournament.connect(tournamentId);
}