from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core import serializers
import json
from datetime import datetime
import sys

from .models import Match, UserData, News, CustomUser, Goal, Tournament

from .utils import registerUser

from django.utils.translation import gettext as _

import logging
logger = logging.getLogger(__name__)

def tournamentCreation(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error user is not logged in.'}, safe=False)
    if request.method != 'POST':
        return JsonResponse({   'err': True,
                    'errMessage': 'Error wrong method used.'}, safe=False)
    tournamentName = request.POST.get('tournamentName')
    isExisting = Tournament.objects.filter(title=tournamentName).first()
    if isExisting and isExisting.status != 'closed':
        return JsonResponse({   'err': True,
                    'errMessage': 'Error an opened tournament already have the same name.'}, safe=False)
    if not tournamentName:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error please specify a tournament name.'}, safe=False)
    if len(tournamentName) > 124:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error tournament name must be under 124 characters.'}, safe=False)
    ownerTournaments = Tournament.objects.filter(creator=request.user, status='open')
    if len(ownerTournaments) >= 3:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error you already have 3 or more opened tournaments.'}, safe=False)
    newTournament = Tournament.objects.create(title=tournamentName, creator=request.user)
    if request.POST.get('autoRegister'):
        newTournament.player_1 = request.user
    newTournament.save()
    return JsonResponse({ 'err': False,
                    'errMessage': 'Tournament successfully created.',
                    'id': newTournament.id }, safe=False)

def tournamentDelete(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error user is not logged in.'}, safe=False)
    if request.method != 'POST':
        return JsonResponse({   'err': True,
                    'errMessage': 'Error wrong method used.'}, safe=False)
    tournamentId = request.POST.get('tournamentId')
    if not tournamentId or not tournamentId.isnumeric():
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong tournament id.'}, safe=False)
    try:
        tournament = Tournament.objects.get(id=int(tournamentId))
        if tournament.status != 'open':
            return JsonResponse({   'err': True,
                'errMessage': 'Error can\'t delete an opened tournament.'}, safe=False)
        tournament.delete()
        return JsonResponse({ 'err': False,
                    'errMessage': 'Tournament successfully deleted.'}, safe=False)
    except:
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong tournament id.'}, safe=False)

def tournamentRegister(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error user is not logged in.'}, safe=False)
    if request.method != 'POST':
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong method used.'}, safe=False)
    tournamentId = request.POST.get('tournamentId')
    if not tournamentId or not tournamentId.isnumeric():
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong tournament id.'}, safe=False)
    slot = request.GET.get('slotNb')
    if not slot or not slot.isnumeric():
        return JsonResponse({   'err': True,
            'errMessage': 'Error wrong slot number.'}, safe=False)
    try:
        tournament = Tournament.objects.get(id=int(tournamentId))
        response = registerUser(request, tournament, int(slot))
        return response
    except:
        return JsonResponse({   'err': True,
                'errMessage': 'Error try again later.'}, safe=False)

def tournamentValidate(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                    'errMessage': 'Error user is not logged in.'}, safe=False)
    if request.method != 'POST':
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong method used.'}, safe=False)
    tournamentId = request.POST.get('tournamentId')
    if not tournamentId or not tournamentId.isnumeric():
        return JsonResponse({   'err': True,
                'errMessage': 'Error wrong tournament id.'}, safe=False)
    try:
        tournament = Tournament.objects.get(id=int(tournamentId))
        if not tournament.creator == request.user:
            return JsonResponse({   'err': True,
                'errMessage': 'Error you are not the owner.'}, safe=False)
        if tournament.status != 'open':
            return JsonResponse({   'err': True,
                'errMessage': 'Error tournament is not open.'}, safe=False)
        tournament.status = 'inProgress'
        tournament.save()
        return JsonResponse({   'err': False,
                'errMessage': 'Tournament is now in progress.'}, safe=False)
    except:
        return JsonResponse({   'err': True,
                'errMessage': 'Error try again later.'}, safe=False)