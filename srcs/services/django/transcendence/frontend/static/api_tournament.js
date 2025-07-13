
function tournamentValidateHandler(object, tournamentId)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/tournament/validate",
        body: formToSend,
    }).then(function(response) {
        if (response.err === false)
            loadPage('tournament', "id=" + tournamentId, true);
        else
            displayError(response.errMessage, "error-wrap")
    })
}

function tournamentRegisterHandler(object, slotNb, tournamentId)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/tournament/register",
        params: {'slotNb': slotNb},
        body: formToSend,
    }).then(function(response) {
        if (response.err === false)
            loadPage('tournament', "id=" + tournamentId, true);
        else
            displayError(response.errMessage, "error-wrap")
    })
}

function tournamentDeleteHandler(object)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/tournament/delete",
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
            loadPage('tournament');
        else
            displayError(response.errMessage, "error-wrap");
    })
}

function tournamentCreateHandler(object)
{
    const formToSend = new FormData(object);


    m.request({
        method: "post",
        url: "/api/tournament/create",
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
            loadPage('tournament', "id=" + response.id);
        else
            displayError(response.errMessage, "error-wrap");
    })
}