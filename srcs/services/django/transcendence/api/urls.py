from django.urls import path

from . import viewsAPI 
from . import viewsUserManagement
from . import viewsTournament

urlpatterns = [

    ### API ###

    path("matches/<str:username>", viewsAPI.returnMatchesFromUsername),
    path("userdata/<str:id>", viewsAPI.getUserDataById),
    path("news/", viewsAPI.getTheNews),
    path("ladder/", viewsAPI.getLadder),
    path("search/", viewsAPI.getSearch),
    path("stats/", viewsAPI.getStatsForCharts),
#    path("isLoggedIn/", viewsAPI.hasUserSession),

        ### TOURNAMENT ###

        path("tournament/create", viewsTournament.tournamentCreation),
        path('tournament/delete', viewsTournament.tournamentDelete),
        path('tournament/register', viewsTournament.tournamentRegister),
        path('tournament/validate', viewsTournament.tournamentValidate),

        ### END TOURNAMENT ###       
    
    ### USER MANAGEMENT ###

    path('login/', viewsUserManagement.login_view),
    path('logout/', viewsUserManagement.logout_view),
    path('register', viewsUserManagement.register_view),
    path('OAuth/', viewsUserManagement.OAuth),
    path('update', viewsUserManagement.updateUserData),
    path('delete', viewsUserManagement.deleteUser),

        ### FRIENDSHIP MANAGEMENT ###

        path('friendRequest', viewsUserManagement.sendFriendRequest),
        path('deleteFriendRequest', viewsUserManagement.deleteFriendRequest),
        path('deleteFriendship', viewsUserManagement.deleteFriendship),

        ### END FRIENDSHIP MANAGEMENT ###

    ### END USER MANAGEMENT ###

    ### END API ###
]