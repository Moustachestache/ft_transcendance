from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search, name="search"),
    path("play/", views.play, name="play"),
    path("ladder/", views.ladder, name="ladder"),
    path("profile/", views.profile, name="profile"),
    path("updateProfile/", views.updateProfile, name="updateProfile"),
    path("match/", views.match, name='match'),
    path('tournament/', views.tournament, name='tournament'),
    path('createTournament/', views.createTournament, name='createTournament'),
    path("search", views.search, name='search'),
    path("register/", views.register, name="register"),
    path("friend/", views.friend),

    # simple functions
    path("login/", views.login, name="login"),

    # language placeholder
    # path("language/", include("django.conf.urls.i18n")),
    path("language/<str:lang>/", views.language, name="language/{lang}"),
    # path("language/", views.language, {"lang":"none"}, name="language"),
]