
class Match
{
    constructor(routing)
    {
        this.routing = routing;
        this.socket = null;
    }

    connect(matchId, data)
    {
        if (this.socket && this.socket.readyState === WebSocket.OPEN)
        {
            console.log("Client already connected to matchmaking.");
            return ;
        }

        this.socket = new WebSocket('wss://' + window.location.host + this.routing + matchId + '/');

        this.data = data

        this.socket.onopen = () => {
            console.log("Connected to match, id=" + matchId + ".");
            _initInterface(this.data)
            drawPoints()
            resetGame()
            this.connected = true;
        };

        this.socket.onmessage = (event) => {
            pongHandler(event.data);
        }

        this.socket.onclose = () => {
            gameInfo.isRunning = 0;
            this.socket = null;
            fetchUserdata()
        }
    }

    disconnect()
    {
        if (this.socket && this.socket.readyState === this.socket.OPEN)
        {
            this.socket.close();
            this.socket = null;
            this.data = null;
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

    serializeAndSend(object)
    {
        jsonObject = JSON.stringify(object);
        this.send(jsonObject);
    }

}