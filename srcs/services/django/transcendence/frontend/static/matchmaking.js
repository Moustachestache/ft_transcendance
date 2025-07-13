
class Matchmaking
{
    constructor(routing)
    {
        this.routing = routing;
        this.socket = null;
    }

    connect()
    {
        if (this.socket && this.socket.readyState === WebSocket.OPEN)
        {
            console.log("Client already connected to matchmaking.");
            return ;
        }

        if (this.socket && this.socket.readyState !== WebSocket.CLOSED)
            this.socket.close();

        this.socket = new WebSocket("wss://" + window.location.host + this.routing);

        this.socket.onopen = () => {
            console.log("Connected to matchmaking.");
            this.connected = true;
            this.send("enter_casual");
        };

        this.socket.onmessage = (event) => {
            let obj = JSON.parse(event.data);
            if (!obj.match_id)
            {
                console.log("Error no match id received")
                this.disconnect();
                return ;
            }
            this.disconnect();
            match.connect(obj.match_id, obj);
        };

        this.socket.onclose = () => {
            this.socket = null;
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
        }
        else
            console.log("Send error, the socket is closed.");
    }
}

function startMatchmaking(tournamentId) {
    matchmaking.connect(tournamentId)
}

function leaveMatchmaking()
{
    matchmaking.disconnect();
    match.disconnect(); // testing
}