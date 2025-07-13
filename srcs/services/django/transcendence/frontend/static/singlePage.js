/*
    singlePage.js
    single page management file
    gestion de l'aspect single-page du site (chargement de pages sans recharger toute la page etc.)
*/
//  define
const   _pageSize = {"ladder": 3, "": 2}
const   _pageOffset = 0;
const   _pageOffsetValue = 0;
const   _pageList = ["", "ladder", "login", "logout", "play", "profile", 'tournament', 'createTournament', "updateProfile", "match", "register", "search", "friend", "language"]

//  init global variable
var     _user = null;
var     _page = {name: ""};
        _page = {name: "", size: _pageSize[_page.name], offset: _pageOffset};

//  setting up CSRF
const   _csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

//  this variable saves the previously rendered "infinite scroll" items (news, players in ladder etc.)
//  it is reset when we get to a new page (see: loadPage())
var     _previousRenders = [];

//  updates var user by calling api/login
//  and updates html on page with new user data

function handleNavigation()
{
    if (window.location.hash.substring(2) == "")
        loadPage('news', '');
    const hash = window.location.hash.substring(2);
    const [path, args] = hash.split('?');
    loadPage(path, args);
}

/* window.addEventListener('DOMContentLoaded', handleNavigation); */

window.addEventListener('hashchange', handleNavigation);

function fetchUserdata()
{
    jsonUserData = m.request({
        method: "GET",
        url: "/api/login/",
        withCredentials: true,
    })
    jsonUserData.then(function(response){
        updateUserdata(response);
        updateUserdataOnPage();
        updateUserdataOnToggle();
    })
    jsonUserData.finally(function(response){
        cookiePopup()
    })
}

function updateUserdata(response)
{
    try
    {
        if (response.err === false)
        {
            response.userData = JSON.parse(response.userData);
            response.userData = response.userData[0];
            _user = {
                date:       response.creation_date,
                name:       response.username,
                id:         response.userData.fields.user,
                isOAuth:    response.userData.fields.isOAuth,
                score:      response.userData.fields.score,
                lang:       response.userData.fields.language,
                image:      (response.userData.fields.profile_pic ? "/media/" + response.userData.fields.profile_pic : "/static/profileDefault.png")
            }
        }
        localStorage.setItem("_cookie", 1);
    }
    catch
    {
        _user = {
            date:       "error",
            name:       "error",
            id:         "error",
            isOAuth:    "error",
            score:      "error",
            lang:       "error",
            image:      "error"
        }
        if (!localStorage.getItem("_cookie"))
        {
            localStorage.setItem("_cookie", 0);
        }
    }
}

//  updates userdata on the page (widget) with user. information
//  uses mythril's elements to not re-render things that havent changed
function updateUserdataOnPage()
{
    if (_user === null)
        return ;
    target = document.getElementById("nav-profile")
    divUserWidget = m("div.row rounded ps-2 pb-2 pt-2", {"id": "nav-profile-content", onclick: () => loadPage("profile")},[
        m("div.row", [
            m("div.col-7", [
                m("h3", {"id": "nav-profile-username"}, [
                    (_user.isOAuth ? m("img.nav-profile-42logo", {"src": "/static/42-logo.svg"}, "") : m("#", "")),
                    m("span", _user.name)
                ]),
                m("div", {"id": "nav-profile-score"}, "score: " + _user.score),
                //m("div", {"id": "nav-profile-rank"}, "rank: " + _user.rank)
            ]),
            m("div.col-5", m("img", {"class": "rounded-circle", "id": "nav-profile-img", "src": _user.image}, "")),
        ])
    ]);
    m.render(target, divUserWidget);
}

function updateUserdataOnToggle()
{
    if (_user === null)
        return ;
    target = document.getElementById("nav-profile-toggle")
    divUserWidget = m("div.row rounded p-2", {"id": "nav-profile-content"},[
        m("div.row", [
            m("div.col-7.d-none.d-sm-block.d-md-block", [
                m("h4", {"id": "nav-profile-username"}, [
                    (_user.isOAuth ? m("img.nav-profile-42logo", {"src": "/static/42-logo.svg"}, "") : m("#", "")),
                    m("span", _user.name)
                ]),
                m("div", {"id": "nav-profile-score"}, "score: " + _user.score),
                //m("div", {"id": "nav-profile-rank"}, "rank: " + _user.rank)
            ]),
            m("div.ms-4.ms-sm-0.ms-md-0.col-10.col-sm-5.col-md-5", m("img", {"class": "rounded-circle border border-2 border-white", "id": "nav-profile-img", "src": _user.image}, "")),
        ])
    ]);
    m.render(target, divUserWidget);
}

//  reloads page when accessing from a "url"
//  example: loading the site from localhost/!#player will reload the page to /player/
function pageReload()
{
    param = window.location.hash;
    if (param.replace("#!", "") == false)
        return ;
    url = param.split('?');
    if (url.length > 2)
    {
        m.route.set('');
        return ;
    }
    else if (url.length === 1)
        loadPage(url[0].replace("#!", ""), null, 1); // I added 1 to load page so it forces the reload
    else
        loadPage(url[0].replace("#!", ""), url[1], 1);
}

function    vanish(element)
{
    htmlElement = document.getElementById(element);
    if (htmlElement == false)
        return ;
    m.render(htmlElement, m("#", ""));
}

function    displayError(message, errorType)
{
    htmlTarget = document.getElementById("error-wrap");
    htmlTarget.onclick = function(e) {
        e.preventDefault();
    }

    let htmlErrorElement = m("div.row visible alert alert-danger", {"id": "error-content", "error-key": Math.random()}, [
        m("div.col-1 text-center",
            m.trust("<a href=\"#\" onclick=\"vanish('error-wrap')\"><i class=\"bi bi-x-square\"></i></a>")),
        m("div.col-11", {"id": "error-wrap-text"}, message),
    ]);

    m.render(htmlTarget, htmlErrorElement);
}

function    setPageInfo(page, args)
{
    _page.name = page;
    _page.size = (_pageSize[page] ? _pageSize[page] : 0);
    _page.offset = _pageOffset;
    _previousRenders = []
    _page.args = args;
}

function    loadPage(page, args, ForceReload)
{
    //  stops <a> from reloading
    document.getElementById("nav-link").onclick = function(e) {
        e.preventDefault();
    }

    //  security to not reload shit when dont need to
    //  if page loaded == the has in the title, and ahs no args,_page.name
    //      dont reload because were accessing the same thing.
    if (!ForceReload && page == _page.name && _page.args == args)
        return ;

    if (_pageList.findIndex((e) => e == page) == -1)
    {
        window.location.replace(location.origin);
        return ;
    }

    var getArgs = m.parseQueryString(args)
    try {
        if (getArgs.userId == _user.id)
            getArgs = null;
    } catch (e) {}

    // unload pong when leaving play
    if (_page.name == "play" && page != "play")
        stopPong();

    query = m.request({
        method: "GET",
        url: page + "/",
        async: "false",
        params: getArgs,
        extract: function(xhr) {return {status: xhr.status, body: xhr.responseText}}
    })
    .then(function(response){
        if (response.status >= 400)
            displayError("error: server-side error", "error-warning");
        else
        {
            var pageComponent = {
/*                 oncreate: function(vnode) {
                    if(page === 'play') {
                        // entrypoint vers pong
                        startPong();
                        // startGame(pongFunnyDraw);
                    }
                },
                onremove: function(vnode) {
                    //  exit point
                    stopPong();
                    //stopGame();_page.name
                }, */
                view: function() {
                    return m("div", m.trust(response.body));
                }
            };
            setPageInfo(page, args);
            m.route.set(page, getArgs);
            m.mount(document.getElementById("content"), pageComponent);
        }
    })
    .finally(function(){
        runPageSpecificTrigger();
        vanish('error-wrap'); // remove error notification when changing page
        if (_page.name === 'match')
            loadCharts(getArgs.matchId)
        fetchUserdata()
    })
}

function registerHandler(object)
{
    const formToSend = new FormData(object);

    m.request({
        method: "post",
        url: "/api/register",
        body: formToSend,
    }).then(function(response)
    {
        tryCatchReload(response, () => displayError(response.errMessage, "error-warning"));
    })
}

///////////////////////////////////////////////////////////////////
//      very lazy account generator
/*         function    generateName()
        {
            let r = (Math.random() + 1).toString(36).substring(7);

            return r + "@fake.fake";
        }

        var randomStr = generateName();

        function    letsgo()
        {
            generateName()
            var inputs = document.getElementsByTagName('input');
            var i = 0;

            do {
                if (inputs[i].name != "csrfmiddlewaretoken")
                    inputs[i].value = randomStr;
                i++;
            } while (i < inputs.length);
        } */
/******************************************************************/

function loginHandler(object)
{
    var formData = new FormData(object);

    m.request({
        method: "post",
        url: "/api/login/",
        body: formData,
    })
    .then(function(response) {
        tryCatchReload(response, () => displayError(response.errMessage, "error-warning"));
    })
}

//  async call to /logout
//      AND page reload when logged out
function logoutHandler()
{
    m.request({
        method: "get",
        url: "/api/logout",
    })
    .then(function(response){
        localStorage.clear();
        tryCatchReload(response, null)
    });
}

function tryCatchReload(response, catchFunction)
{
    try
    {
        if (response.err === false)
        {
            try
            {
                if (arguments.size() == 2)
                {
                    updateUserdata(response);
                    loadPage(arguments[2])
                }
            }
            catch (e)
            {
                window.location.replace(location.origin);
            }
        }
        else
            try
            {
                displayError(response.errMessage, "error-wrap");
            } catch (e) {}
    }
    catch (e)
    {
        if (catchFunction != null)
            catchFunction();
    }
}

//  for switching languages. calls to /l18n/set_lang/ with post info of
//  "language" = shortcode (allowed are: fr, en, ka, uk, egy)
function    setLang(formObject)
{
    var formData = new FormData(formObject);

    m.request({
        method: "post",
        url: "/i18n/setlang/",
        body: formData,
    })
    .then(function(response){
    })
    .finally(function(f){
        location.replace(location.href)
    })
}

//  launches when site loads for first time.
//  inits user
//  checks page path
//  forces cookies acceptance
function    hello()
{
    _page.name = window.location.hash.split('?')[0].replace("#!", "");
    pageReload();
    fetchUserdata() // <- here we check for cookies after having fetched user info
    //  beurk, mais ne s'applique que a la page blank
    if (_page.name == "")
        runPageSpecificTrigger();
}