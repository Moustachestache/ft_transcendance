class Player
{
    constructor(keyUp, keyDown)
    {
        this._paddle = new Paddle(keyUp, keyDown);
        this._username = "";
        this._userpic = "";
    }

    _init()
    {
        this._paddle._init()
    }

    _destroy()
    {
        this._paddle._destroy();
    }

    setUsername(val)
    {
        this._username = val;
    }

    setUserpic(val)
    {
        this._userpic = val;
    }

    resize()
    {
        this._paddle.resize();
    }
}