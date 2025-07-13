//  cookie management
//  with bootstrap modal
//  bootstrap modal id is #cookieModal 
//  more: https://stackoverflow.com/questions/11404711/how-can-i-trigger-a-bootstrap-modal-programmatically

const   cookieModal = new bootstrap.Modal(document.getElementById('cookieModal'), {});

function    cookiePopup()
{
    if (!localStorage.getItem("_cookie") || !_user)
    {
        cookieModal.show();
        //  dont ask me why this has to be here
        //  but it has to
        //  because the modal adds a right padding to the body element ...
        document.getElementsByTagName("body")[0].style.paddingRight = "0px";
    }
}

function    cookieDismiss()
{
    localStorage.setItem("_cookie", 1);
}