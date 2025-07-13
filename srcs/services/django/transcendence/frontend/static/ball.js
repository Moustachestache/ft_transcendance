class Ball
{
    constructor()
    {
        this.speed = 69;
        this.direction = 42;
        this.xpos = gameInfo.pongCanvasGame.width / 2;
        this.ypos = gameInfo.pongCanvasGame.height / 2;
        this.size = 15;
        this.newSize = 15;
    }

    _init()
    {
        this.newSize = this.size * gameInfo.pongCanvasGame.xRatio;
        this.redraw()
    }

    redraw()
    {
        gameInfo.pongCanvasGameContext.beginPath();
        gameInfo.pongCanvasGameContext.arc(this.xpos, this.ypos, this.newSize, 0, 2 * Math.PI);
		gameInfo.pongCanvasGameContext.fillStyle = "white";
		gameInfo.pongCanvasGameContext.fill();
    }

    moveTo(x, y)
    {
        this.xpos = x;
        this.ypos = y;
        
        //  redraw
        this.redraw()
    }

    resize()
    {
        this.newSize = this.size * gameInfo.pongCanvasGame.xRatio;
        this.redraw()
    }
}