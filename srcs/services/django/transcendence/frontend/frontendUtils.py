from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.db.models import Q
from django.urls import reverse
from django.conf import settings

from datetime import timedelta

from django.utils import translation

from api.models import UserData, Match, CustomUser, Goal, Tournament

from django.utils.translation import gettext as _

from api.utils import pairing

import os


import logging
logger = logging.getLogger('django')

#   return a list of language info
#   lang.code / lang.name
def     returnLangTable():
    langTable = []
    for lang in settings.LANGUAGES:
        langTable.append({
            "code": lang[0],
            "name": lang[1]
        })
    return langTable

def displayTournamentUtil(request, tournamentId):
    tournament = Tournament.objects.filter(id=int(tournamentId)).first()
    if not tournament:
        return render(request, 'frontend/displayTournament.html')
    matchesArray = []
    matches = Match.objects.filter(tournament=tournament)
    for match in matches:
        if not match.player_1 or not match.player_2:
            matchesArray = []
            break
        matchesArray.append({
            'id': match.id,
            'winner': match.winner,
            'player_1': match.player_1.username,
            'player_2': match.player_2.username,
            'player_1_score': len(Goal.objects.filter(match=match, player=match.player_1).all()),
            'player_2_score': len(Goal.objects.filter(match=match, player=match.player_2).all()),
            'end_date': match.end_date})
    return render(request, 'frontend/displayTournament.html', { 'tournament': tournament,
                                                                'user': request.user ,
                                                                'matches': matchesArray,
                                                                'status': tournament.status, })

def DisplayListTournament(request):
    listType = request.GET.get('list')
    if listType and listType == 'closed':
        tournaments = Tournament.objects.filter(status='closed').order_by('-creation_date').all()
    elif listType and listType == 'inProgress':
        tournaments = Tournament.objects.filter(status='inProgress').order_by('-creation_date').all()
    else:
        tournaments = Tournament.objects.filter(status='open').order_by('-creation_date').all()
    tournamentsArray = []
    for tournament in tournaments:
        free_slots = sum(
        1 for player in [tournament.player_1, tournament.player_2, tournament.player_3, tournament.player_4]
        if player is None)
        tournamentsArray.append({
            'data': tournament,
            'free_slots': free_slots
        })
    return render(request, "frontend/tournament.html", {
        'tournaments': tournamentsArray,
        'listType': listType})
