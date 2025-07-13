//  utils

//  calculates elapsed time between then and now.
//  ideally then and now are gotten with date.now() and are milliseconds
function    elapsedTime(then, now)
{
    let timeValue = now - then;
    if (timeValue < 0)
        throw ("Operation On Time Resulted In Negative Value");
    return timeValue;
}