
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.core import serializers
import json
from datetime import datetime
import sys
from django.views.decorators.csrf import csrf_exempt

from .models import Match, UserData, News, CustomUser, Goal, Tournament

from .utils import registerUser

from django.utils.translation import gettext as _

import logging
logger = logging.getLogger(__name__)

# Create your views here.

### API ###
def getSearch(request):
    if request.method != 'POST':
        return JsonResponse({'err': True,
                        'errMessage': _("Error please use POST method")})
    querykeyword = request.POST.get('query')
    dbRequest = CustomUser.objects.all().filter(username__icontains=querykeyword)
    data = []
    for items in dbRequest:
            data.append(json.JSONEncoder().encode({
                "username": items.username,
                "id":       items.pk,
            }))
    data = json.JSONEncoder().encode(data)
    if (data):
        return JsonResponse({'err': False,
                        'queryResult': data,
                        'queryKeyword': querykeyword})
    else:
        return JsonResponse({'err': True,
                        'errMessage': (_("no data for query ") + querykeyword)})

def returnMatchesFromUsername(request, username):
    """
    Return all matches for a given username if the user is logged in.
    Supports 'offset' and 'size' get values.
    Offset define the index of the reseach. size define the maximum number of elements returned
    """
    if request.method != 'GET':
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please use GET method.')},
                                safe=False)
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error you must be logged in.')},
                                safe=False)
    try:
        researchUser = CustomUser.objects.get(username=username)
    except:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error the user do not exist.')},
                                safe=False)
    try:
        offset = int(request.GET.get('offset'))
        size = int(request.GET.get('size'))
        if not offset >= 0 or not (size <= 50 and size > 0):
            return JsonResponse({   'err': True,
                                    'errMessage': _('Error please set valid offset and size.')},
                                    safe=False)
    except:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please set valid offset and size.')},
                                safe=False)
    Matchs = Match.objects.filter(Q(player_1=researchUser) | Q(player_2=researchUser)).order_by('-creation_date')[offset:size + offset]
    data = serializers.serialize('json', Matchs)
    return JsonResponse({   'err': False,
                            'Matches': data},
                            safe=False)

def getUserDataById(request, id):
    """
    Return users infos for a given id
    """
    if request.method != 'GET':
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please use GET method.')},
                                safe=False)
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error you must be logged in.')},
                                safe=False)
    try:
        nbId = int(id)
        user = CustomUser.objects.get(id=nbId)
        userData = UserData.objects.filter(user=user)
        data = serializers.serialize('json', userData)
        return JsonResponse({   'err': False,
                                'username': user.username,
                                'userData': data},
                                safe=False )
    except :
        return JsonResponse({   'err': True,
                                'errMessage':_('Unable to retrieve user data.')},
                                safe=False )

def getTheNews(request):
    """
    Return News, no need to be logged in.
    Supports 'offset' and 'size' get values.
    Offset define the index of the reseach. size define the maximum number of elements returned.
    """
    if request.method != 'GET':
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please use GET method.')},
                                safe=False)
    if not request.GET.get('offset') or not request.GET.get('size'):
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please set offset and size.')},
                                safe=False)
    try:
        offset = int(request.GET.get('offset'))
        size = int(request.GET.get('size'))
        if not offset >= 0 or not (size <= 50 and size > 0):
            return JsonResponse({   'err': True,
                                    'errMessage': _('Error please set valid offset and size.')},
                                    safe=False)
        retNews = News.objects.all().order_by("-creation_date")[offset:size + offset]
        flags = {
                    "fr": "🇫🇷",
                    "en": "🇬🇧",
                    "ka": "🇬🇪",
                    "egy": "🐫",
                    "uk": "🇺🇦",
                }
        NewsJson = []
        for items in retNews:
            NewsJson.append(json.JSONEncoder().encode({
                "title":    items.title,
                "content":  items.content,
                "language": items.language,
                "username": items.user,
                "date":     items.creation_date.strftime("%Y - %m - %d"),
                "flag":     flags.get(items.language, "🏴‍☠️")
                }))
        NewsJson = json.JSONEncoder().encode(NewsJson)
        return JsonResponse({   'err': False,
                                'News': NewsJson,},
                                safe=False )
    except Exception as e:
        logger.error(e)
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please set valid offset and size.')},
                                safe=False)

# Song.objects.get(id=1).singer_id
def getLadder(request):
    """
    Return players sorted by score
    Supports 'offset' and 'size' get values.
    Offset define the index of the reseach. size define the maximum number of elements returned.
    """
    if request.method != 'GET':
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please use GET method.')},
                                safe=False)
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error you must be logged in.')},
                                safe=False)
    if not request.GET.get('offset') or not request.GET.get('size'):
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please set offset and size.')},
                                safe=False)
    try:
        offset = int(request.GET.get('offset'))
        size = int(request.GET.get('size'))
        topPlayers = UserData.objects.order_by('-score', 'creation_date')[offset:size + offset]
        position = offset
        ladderJson = []
        for items in topPlayers:
            position += 1
            totalMatches = Match.objects.filter(Q(player_1=items.user) | Q(player_2=items.user)).count()
            totalGoalsFor = Goal.objects.filter(Q(player=items.user)).count()
            totalGoalsAgainst = Goal.objects.filter(Q(opponent=items.user)).count()
            ladderJson.append(json.JSONEncoder().encode({
                'position':             position,
                'userId':               items.user.id,
                'username':             items.user.username,
                'score':                items.score,
                'picture':              items.profile_pic.name,
                'totalMatches':         totalMatches,
                'totalGoalsFor':        totalGoalsFor,
                'totalGoalsAgainst':    totalGoalsAgainst,
                'goalDifference':       totalGoalsFor - totalGoalsAgainst
            }))
        ladderJson = json.JSONEncoder().encode(ladderJson)
        return JsonResponse({   'err': False,
                                'userData': ladderJson},
                                safe=False )
    except:
        return JsonResponse({   'err': True,
                                'errMessage': _('Error please set valid offset and size.')},
                                safe=False)

def getStatsForCharts(request):
    """
    Return all stats and goals for a given matchId.
    This function is made to load the charts data in the js script.
    """
    if request.method != 'GET':
        return JsonResponse({   'err': True,
                        'errMessage': _('Error please use GET method.')}, safe=False)
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
                        'errMessage': _('Error you must be logged in.')}, safe=False)
    if not request.GET.get('matchId'):
        return JsonResponse({   'err': True,
                        'errMessage': _('Error please set the matchId.')}, safe=False)
    matchId = request.GET.get('matchId')
    match = Match.objects.filter(id=matchId).first()
    if match is None:
        return JsonResponse({   'err': True,
                        'errMessage': _('Error match not found.')}, safe=False)
    try:
        all_goals = Goal.objects.filter(match=match)

        goalsPlayer1 = []
        goalsPlayer2 = []

        for goal in all_goals:
            if goal.player_id == match.player_1_id:
                goalsPlayer1.append(str(goal.goalTime))
            else:
                goalsPlayer2.append(str(goal.goalTime))

        matchJson = json.JSONEncoder().encode({
            'usernamePlayer1':  match.player_1.username if match.player_1 else _('Anonymous'),
            'usernamePlayer2':  match.player_2.username if match.player_2 else _('Anonymous'),
            'matchDuration': str(match.matchDuration),
        })
        return JsonResponse({
            'err': False,
            'matchData': matchJson,
            'goalsPlayer1': json.JSONEncoder().encode(goalsPlayer1),
            'goalsPlayer2': json.JSONEncoder().encode(goalsPlayer2),
        }, safe=False)
    except:
        return JsonResponse({   'err': True,
                    'errMessage': _('Error match not found.')}, safe=False)
