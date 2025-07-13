from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseNotFound
from django.db.models import Q
from django.urls import reverse
from django.conf import settings
from django.db import models
from datetime import timedelta

from django.utils import translation

from api.models import UserData, Match, CustomUser, Goal, Tournament, FriendRequest, Friendship

from django.utils.translation import gettext as _

from .frontendUtils import returnLangTable, displayTournamentUtil, DisplayListTournament

from api.utils import pairing, is_user_online

import os

#   debug
import logging
logger = logging.getLogger('django')
#   end debug


def home(request):
    err = request.GET.get("error")
    return render(request, "frontend/home.html", {
        "error": err,
        "languages": returnLangTable()
    })

def login(request):
    return render(request, "frontend/login.html", {
        'clientId' : os.getenv('API_UID'),
        'redirectURI' : os.getenv('API_REDIRECT_URI')
    })

def register(request):
    return render(request, "frontend/register.html", {
        'clientId' : os.getenv('API_UID'),
        'redirectURI' : os.getenv('API_REDIRECT_URI')
    })

#   here onward:
#   must be logged in
def search(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/errorPageNotLoggedIn.html")
    querykeyword = request.GET.get('query')
    if not querykeyword:
        return render(request, "frontend/search.html")
    dbRequest = CustomUser.objects.all().filter(username__icontains=querykeyword)
    resultArray = []
    for items in dbRequest:
        userdataOfItem = UserData.objects.filter(user=items).first()
        resultArray.append({
            "username": items.username,
            "picture":  userdataOfItem.profile_pic,
            "id":       userdataOfItem.user.id,
        })
    return render(request, "frontend/search.html", {"dbRequest": resultArray})

def play(request):
    if request.user.is_authenticated:
        tournaments = Tournament.objects.filter(
            Q(player_1=request.user) | 
            Q(player_2=request.user) | 
            Q(player_3=request.user) | 
            Q(player_4=request.user),
            status="inProgress")
        tournament_list = []
        for tournament in tournaments:
                tournament_list.append({
                    'id': tournament.id,
                    'title': tournament.title,
                    'player_1': tournament.player_1.username,
                    'player_2': tournament.player_2.username,
                    'player_3': tournament.player_3.username,
                    'player_4': tournament.player_4.username,
                    'creator': tournament.creator,
                    'matches': Match.objects.filter(tournament=tournament), })
        return render(request, "frontend/play.html", {
            'tournaments': tournament_list,
            'username': request.user.username,})
    else:
        return render(request, "frontend/errorPageNotLoggedIn.html")

def ladder(request):
    if request.user.is_authenticated:
        return render(request, "frontend/ladder.html")
    else:
        return render(request, "frontend/errorPageNotLoggedIn.html")

def profile(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/profile.html")
    userId = request.GET.get('userId')
    if userId and not userId.isnumeric():
        return render(request, "frontend/profile.html")
    if userId:
        user = CustomUser.objects.filter(id=userId).first()
    else:
        user = request.user
    totalMatches = Match.objects.filter(Q(player_1=user) | Q(player_2=user)).count()
    userData = UserData.objects.filter(user=user).first()
    ladderPosition = 1
    for item in UserData.objects.filter().order_by('-score'): # this is shit
        if item.user == user:
            break
        else:
            ladderPosition += 1
    matches = []
    for match in Match.objects.filter(Q(player_1=user) | Q(player_2=user)).order_by('-creation_date')[0:10]:
        matches.append({
            'id': match.id,
            'end_date': match.end_date,
            'player_1': match.player_1,
            'player_2': match.player_2,
            'player_1_score': len(Goal.objects.filter(match=match, player=match.player_1).all()),
            'player_2_score': len(Goal.objects.filter(match=match, player=match.player_2).all()),
            'winner': match.winner, })
    try:
        winrate =  (userData.score / totalMatches) * 100
        winrate = round(winrate, 2) # Make sure we don't have more than 2 floating point numbers
    except:
        winrate = 0
    return render(request, "frontend/profile.html", {   'userData': userData,
    'matches': matches,
    'totalMatches': totalMatches,
    'isOwner': True if user == request.user else False,
    'isFriendRequestPending': True if FriendRequest.objects.filter(sender=request.user, receiver=user).exists() else False,
    'isAwaiting': True if FriendRequest.objects.filter(sender=user, receiver=request.user).exists() else False,
    'isFriend': True if Friendship.objects.filter((models.Q(friend_one=request.user, friend_two=user)) | (models.Q(friend_one=user, friend_two=request.user))).exists() else False,
    'ladderPosition': ladderPosition,
    'winRate': winrate})

def updateProfile(request):
    if request.user.is_authenticated:
        return render(request, "frontend/updateProfile.html", {'userData': UserData.objects.get(user=request.user)})
    else:
        return render(request, "frontend/errorPageNotLoggedIn.html")

def match(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/errorPageNotLoggedIn.html")
    try:
        match = Match.objects.get(id=request.GET.get('matchId'))
        if not match.player_1:
            userDataPlayer2 = UserData.objects.filter(user=match.player_2).first()
            userDataPlayer1 = 0
            goalTotal = len(Goal.objects.filter(match=match).all())
            goalsPlayer2 = len(Goal.objects.filter(player=match.player_2, match=match).all())
            goalsPlayer1 = goalTotal - goalsPlayer2
        elif not match.player_2:
            userDataPlayer1 = UserData.objects.filter(user=match.player_1).first()
            userDataPlayer2 = 0
            goalTotal = len(Goal.objects.filter(match=match).all())
            goalsPlayer1 = len(Goal.objects.filter(player=match.player_1, match=match).all())
            goalsPlayer2 = goalTotal - goalsPlayer1
        else:
            goalsPlayer1 = len(Goal.objects.filter(player=match.player_1, match=match).all())
            goalsPlayer2 = len(Goal.objects.filter(player=match.player_2, match=match).all())
            userDataPlayer1 = UserData.objects.get(user=match.player_1)
            userDataPlayer2 = UserData.objects.get(user=match.player_2)

        return render(request, "frontend/match.html", {
            'match': match,
            'winner': match.winner,
            'goalsPlayer1': goalsPlayer1,
            'goalsPlayer2': goalsPlayer2,
            'userDataPlayer1': userDataPlayer1,
            'userDataPlayer2': userDataPlayer2 })
    except:
            return render(request, "frontend/match.html")

def tournament(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/errorPageNotLoggedIn.html")
    tournamentId = request.GET.get('id')
    if tournamentId and tournamentId.isnumeric(): # Display a precise tournament
        return displayTournamentUtil(request, tournamentId)
    else: # Display the tournament list
        return DisplayListTournament(request)

def createTournament(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/errorPageNotLoggedIn.html")
    if request.method != 'GET':
        return HttpResponseNotFound()
    return render(request, "frontend/createTournament.html", { 'user': request.user })



def friend(request):
    if not request.user.is_authenticated:
        return render(request, "frontend/errorPageNotLoggedIn.html")
    listType = request.GET.get('list')
    if listType and listType == 'pending':
        nodesToSend = getPendingRequests(request)
    elif listType and listType == 'all':
        nodesToSend = getAllFriends(request)
    else:
        nodesToSend = getOnlineFriends(request)
    return render(request, "frontend/friend.html", {
        "listType" : listType,
        "nodes" : nodesToSend,
    })

def getPendingRequests(request):
    nodesToSend = []
    nodes = FriendRequest.objects.filter(
            (models.Q(sender=request.user)) |
            (models.Q(receiver=request.user))).all()
    for node in nodes:
        user = node.sender if request.user != node.sender else node.receiver
        nodesToSend.append({
            "username": user.username,
            "id": user.id,
            "profile_pic": UserData.objects.get(user=user).profile_pic,
            "isSender": True if request.user == node.sender else False,
        })
    return nodesToSend


def getOnlineFriends(request):
    nodesToSend = []
    nodes = Friendship.objects.filter(
            (models.Q(friend_one=request.user)) |
            (models.Q(friend_two=request.user))).all()
    for node in nodes:
        user = node.friend_one if node.friend_one != request.user else node.friend_two
        if is_user_online(user):
            nodesToSend.append({
                "username" : user.username,
                "id": user.id,
                "isOnline": is_user_online(user),
                "profile_pic": UserData.objects.get(user=user).profile_pic })
    return nodesToSend

def getAllFriends(request):
    nodesToSend = []
    nodes = Friendship.objects.filter(
            (models.Q(friend_one=request.user)) |
            (models.Q(friend_two=request.user))).all()
    for node in nodes:
        user = node.friend_one if node.friend_one != request.user else node.friend_two
        nodesToSend.append({
            "username" : user.username,
            "id": user.id,
            "isOnline": is_user_online(user),
            "profile_pic": UserData.objects.get(user=user).profile_pic })
    return nodesToSend

# language
def language(request, lang):
    translation.activate(lang)
    response = HttpResponseRedirect("home")
    response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
    return HttpResponse(response)