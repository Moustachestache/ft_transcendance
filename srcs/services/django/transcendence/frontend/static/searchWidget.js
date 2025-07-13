var     _searchInputTimer = Date.now();

var     _searchInputHtmlElement = document.getElementById("nav-search-input");
var     _parentSearchInputHtmlElement = document.getElementById("nav-search");
var     _navHtmlElement = document.getElementById("nav");
var     _searchInputResultHtmlElement = document.getElementById("nav-search-result");

var     _currentSearchResults = [];

//  id=nav-search-result
function    flushSearchResultWidget()
{
    m.render(_searchInputResultHtmlElement, m(""));
    _currentSearchResults = [];
    emptySearchBar();
}

function    updateSearchResultWidget(jsonResponse)
{
    let htmlListArray = [];

    for (i = 0; i < jsonResponse.length; i++)
    {
        let serializedItem =  JSON.parse(jsonResponse[i]);

        htmlListArray.push(m(
            "li.list-group-item", {
                onclick: () => loadPage('profile', 'userId=' + serializedItem.id)
            }, [m("i.bi bi-person-fill"),
                m("span.ms-2", serializedItem.username)]
            ));
    }
    if (jsonResponse.length == 0)
        htmlListArray.push(m("li.list-group-item", m("i.bi bi-person-x")));
    m.render(_searchInputResultHtmlElement, m("ul.list-group", htmlListArray));
}

function    emptySearchBar()
{
    _searchInputHtmlElement.value = "";
}

function    searchHandler(query)
{
    var postData = new FormData();

    postData.append("query", query);

    m.request({
        method: "post",
        url: "/api/search/",
        body: postData,
        headers: {
            "X-CSRFToken": _csrftoken
        },
    })
    .then(function(response){
        jsonResponse = JSON.parse(response.queryResult);
        updateSearchResultWidget(jsonResponse);
    });
}

//  search bar JS
//  id="nav-search-input"
//  setup event listener for keypress, and then specifically enter - in search bar (see ID)
//  add 3s wait for refresh
try {
    _searchInputHtmlElement.addEventListener("keyup", function(e) {
        //  updates search suggestion every second
        if (_searchInputHtmlElement.value == false)
            flushSearchResultWidget();
        else if (e.key === "Enter")
        {
            loadPage("search", ("query=" + _searchInputHtmlElement.value));
            //  then: loadpage("search" + info)
            flushSearchResultWidget()
        }
        else
            searchHandler(_searchInputHtmlElement.value);
    });
    
} catch (error) {
    console.log("_searchInputHtmlElement does not exist. \r\nThis page will not display a search bar.");
}
