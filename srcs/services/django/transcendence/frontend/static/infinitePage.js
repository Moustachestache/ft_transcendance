//  https://developer.mozilla.org/en-US/docs/Web/API/Intersection_Observer_API
//  bible: https://w3c.github.io/IntersectionObserver/#intersection-observer-interface
//  regarding infinite scroll and triggers
//  infinite scroll observer and related function
//  <div id="scrollObserverElement"/>
var     _currentScrollCallback = function foo() {}
var     _observerInteresctionStatus = true;
const   _observerElement = document.getElementById("scrollObserverElement");
const   _observer = new IntersectionObserver(function(e){
    _observerInteresctionStatus = e[0].isIntersecting;
    if (_observerInteresctionStatus == true)
        _currentScrollCallback();
});

function playAnimation()
{
    let target = document.getElementById("loadingAnim");
    let animationDiv = m("div.row", {"id": "loadingPong"},
        m("div.loadingcontent", [
            m("div.player_one"),
            m("div.player_two"),
            m("div.ball"),
    ]));
    m.render(target, animationDiv);
}

//  sets up triggers for certain pages.
//  ie: on homepage (news), triggers loadNews() once onload
//  or: on ladder, loads first chunk of ladder before running, and sets up a scroll trigger
function    runPageSpecificTrigger()
{
    switch (_page.name)
    {
        default:
            //  has no need for scroll load, so set to null (unsets if there was a previous value);
            _currentScrollCallback = function foo(){}
            break ;
        case "":
            _currentScrollCallback = () => loadNews();
            break ;
        case "ladder":
            _currentScrollCallback = () => loadLadder();
            break ;
        case "play":
            startPong();
            break;
    }
    _observer.unobserve(_observerElement);
    _observer.observe(_observerElement);
}

function stopAnimation()
{
    let target = document.getElementById("loadingAnim");
    m.render(target, m("#", ""));
}

//  https://127.0.0.1:8433/api/news/?size=2&offset=0
function loadNews()
{
    if (_page.name != "")
        return ;

    playAnimation();

    m.request({
        method: "get",
        url: "/api/news/",
        async: "false",
        params: {size: _page.size, offset: _page.offset},
    })
    .then(function(response) {
        _page.offset += _page.size;
        if (response.err == true)
        {
            displayError(err.message, "error-wrap");
            return ;
        }
        newsArray = JSON.parse(response.News);
        let     targetElement = document.getElementById("content-news");
        let i = 0
        for (; i < newsArray.length; i++)
        {
            thisArray = JSON.parse(newsArray[i]);

            let newDiv = m("div.border mb-3 rounded-5 bg-white", [
                m("div.row d-flex justify-content-between", [
                    m("div.fs-3 col-10", thisArray.title),
                    m("div.col-1 fs-3 me-3", thisArray.flag)
                ]),
                m("div.news-date", [
                    m("div.row", [
                        m("div.col-2", [
                            m("i.bi bi-person-circle"),
                            m("span", " " + thisArray.username + " ")
                        ]),
                        m("div.col-2", [
                            m("i.bi bi-calendar3"),
                            m("span", " " + thisArray.date)
                        ])
                    ]),
                ]),
                m("div.news-text pt-3", [
                    m("p", [
                        m.trust(thisArray.content)
                    ])
                ])
            ]);
            _previousRenders.push(newDiv);
        }
        if (_previousRenders.length > 0)
            m.render(targetElement, _previousRenders);
        if (i == 0)
        {
            _observerInteresctionStatus = false;
            _observer.unobserve(_observerElement)
            return ;
        }
    })
    .finally(function(e) {
        stopAnimation();
        if (_observerInteresctionStatus == true)
            _currentScrollCallback.apply()
    })
}

function loadLadder()
{
    if (_page.name != "ladder" || !_user)
        return ;

    playAnimation();

    m.request({
        method: "get",
        url: "/api/ladder/",
        async: "false",
        params: {size: _page.size, offset: _page.offset},
    })
    .then(function(response) {
        _page.offset += _page.size;
        if (response.err == true)
        {
            displayError(response.errMessage, "error-wrap");
            _observerInteresctionStatus = false;
            _observer.unobserve(_observerElement)
            return ;
        }
        ladderArray = JSON.parse(response.userData).map(user => JSON.parse(user));
        console.log(ladderArray);
        let     targetElement = document.getElementById("content-ladder");
        let i = 0
        let currentDiv;
        let newDiv = [];
        for (; i < ladderArray.length; i++)
        {
            let thisItem = ladderArray[i]

            currentDiv = m("tr", {class: "pointer-hover text-center", onclick: () => loadPage('profile', 'userId=' + thisItem.userId)}, [
                    m("td", {class: "align-middle text-center"}, [thisItem.position]),
                    m("td", [
                        m("img.img-fluid rounded align-middle",{style: "max-width: 30px;", src: (thisItem.picture ? "/media/" + thisItem.picture : "/static/profileDefault.png")})
                    ]),
                    m("td", {class: "align-middle text-center"}, [thisItem.username]),
                    m("td", {class: "align-middle text-center"}, [thisItem.totalMatches]),
                    m("td", {class: "align-middle text-center"}, [thisItem.score]),
                    m("td", {class: "align-middle text-center"}, [thisItem.totalMatches - thisItem.score]),
                    m("td", {class: "align-middle text-center"}, [thisItem.totalGoalsFor]),
                    m("td", {class: "align-middle text-center"}, [thisItem.totalGoalsAgainst]),
                    m("td", {class: "align-middle text-center"}, [thisItem.goalDifference]),
            ]);
            console.log(thisItem);
            newDiv.push(currentDiv);
        }
        if (i == 0)
        {
            _observerInteresctionStatus = false;
            _observer.unobserve(_observerElement)
            return ;
        }
        _previousRenders.push(newDiv);
        m.render(targetElement, _previousRenders);
    })
    .finally(function(e) {
        if (_observerInteresctionStatus == true)
            _currentScrollCallback.apply()
        stopAnimation();
    })
}
