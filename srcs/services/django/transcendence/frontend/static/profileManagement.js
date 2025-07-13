
function displayProfile()
{
    if (!_user)
        return
    let targetElement = document.getElementById("profile-content");
    
}

function updateHandler(object)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/update",
        body: formToSend,
    }).then(function(response)
    {
        updateUserdata(response);
        updateUserdataOnPage();
        tryCatchReload(response, () => displayError(response.errMessage, "error-warning"), "profile");
    })
}

function deleteUserHandler(object, errLabel)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/delete",
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
        {
            errLabel.classList.remove("text-danger")
            errLabel.innerHTML = response.errMessage
            deleteButton = document.getElementById("deleteConfirm")
            if (deleteButton)
                deleteButton.disabled = true;
            setTimeout(function() {
                tryCatchReload(response, () => displayError(response.errMessage, "error-warning"), "");
            }, 3000);
        }
        else{
            errLabel.innerHTML = response.errMessage
        }
    })
}

function sendFriendRequest(object, userId)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/friendRequest",
        params: {'friendId': userId},
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
			pageReload();
        else
            displayError(response.errMessage, "error-wrap")
    })
}

function deleteFriendRequest(object, userId)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/deleteFriendRequest",
        params: {'friendId': userId},
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
            pageReload();
        else
            displayError(response.errMessage, "error-wrap")
    })
}

function deleteFriendship(object, userId)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/deleteFriendship",
        params: {'friendId': userId},
        body: formToSend,
    }).then(function(response)
    {
        if (response.err === false)
			pageReload();
        else
            displayError(response.errMessage, "error-wrap")
    })
}