class Paddle
{
    constructor(keyControlUp, keyControlDown, userId)
    {
        this._keyControlUp = keyControlUp;
        this._keyControlDown = keyControlDown;
        this._userId = userId;
        this._moveStatus = 0;
        this._lastPress = 0;
        this._width = 25;
        this._height = 200;
        this._ypos = 0;
        this._xpos = 0;
        this.score = 0;
        this.isInit = 0;

        this._eventKeyDown = (keydown) => {
            if (this._moveStatus == 1)
                return ;
            this._moveStatus = 1;
            this._lastPress = Date.now();
            if (keydown.key == this._keyControlDown)
                this.paddleMovedown(event)
            if (keydown.key == this._keyControlUp)
                this.paddleMoveup(event)
        };

        this._eventKeyUp = (event) => {
            this._moveStatus = 0;
            let pressTime = Date.now() - this._lastPress;
            if (event.key == this._keyControlDown)
                this.stopPaddleMovedown(event, pressTime)
            if (event.key == this._keyControlUp)
                this.stopPaddleMoveup(event, pressTime)
        };
    }

    _init()
    {
        this._ypos = (gameInfo.pongCanvasGame.height / 2) - ((this._height * gameInfo.pongCanvasGame.xRatio) / 2)
        document.addEventListener('keydown', this._eventKeyDown);
        document.addEventListener('keyup', this._eventKeyUp);
        if (this._userId == -1)
            this._xpos = gameInfo.pongCanvasGame.width - (this._width * gameInfo.pongCanvasGame.xRatio);
        this.redraw()
        this._init = 1;
    }

    _destroy()
    {
        document.removeEventListener('keydown', this._eventKeyDown);
        document.removeEventListener('keyup', this._eventKeyUp);
    }

    redraw()
    {
        gameInfo.pongCanvasGameContext.fillStyle = "white";
        gameInfo.pongCanvasGameContext.fillRect(this._xpos, this._ypos * gameInfo.pongCanvasGame.xRatio, this._width * gameInfo.pongCanvasGame.xRatio, this._height * gameInfo.pongCanvasGame.xRatio);
    }

    paddleMoveup(event)
    {
        match.send("Start Up")
    }

    paddleMovedown(event)
    {
        match.send("Start Down")
    }

    stopPaddleMoveup(event, pressTime)
    {
        match.send("Stop Up")
    }

    stopPaddleMovedown(event, pressTime)
    {
        match.send("Stop Down")
    }

    resize()
    {
        if (this._userId == -1)
            this._xpos = gameInfo.pongCanvasGame.width - (this._width * gameInfo.pongCanvasGame.xRatio);
        this.redraw()
    }
}
