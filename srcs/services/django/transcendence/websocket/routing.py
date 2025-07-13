from django.urls import re_path
from . import matchmakingConsumer, matchConsumer, tournamentConsumer

websocket_urlpatterns = [
    re_path(r'ws/matchmaking/', matchmakingConsumer.Matchmaking.as_asgi()),
    re_path(r'ws/tournament/(?P<tournamentId>\w+)/$', tournamentConsumer.TournamentConsumer.as_asgi()),
    re_path(r'ws/match/(?P<matchId>\w+)/$', matchConsumer.MatchConsumer.as_asgi()),
]