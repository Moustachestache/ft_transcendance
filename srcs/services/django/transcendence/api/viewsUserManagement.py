from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout, password_validation
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core import serializers
from django.core.validators import validate_email
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import models

from pathlib import Path
import os, requests
import json
import re

from .models import Match, UserData, CustomUser, Tournament, Friendship, FriendRequest
from .utils import getImageExtention, createSquareThumbnail
from .utilsUserManagement import registerOAuth, loginOAuth, updateProfilePicture, checkAndSetPassword

from django.utils.translation import gettext as _

### LOGIN/LOGOUT/REGISTER ###

def login_view(request):
    """
    Login through API, client must send 'email' and 'password'.
    Returns the user's informations into json.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            return JsonResponse({   'err': True,
                                'errMessage': _('User is already logged in.')},
                                safe=False)
        try:
            email = request.POST['email']
            password = request.POST['password']
        except:
            return JsonResponse({   'err': True,
                                'errMessage': _('Error wrong email or password.')},
                                safe=False)
        user = authenticate(request, username=email, password=password) # username=email, this is due to the CustomUser
        if user is None:
            return JsonResponse({   'err': True,
                                'errMessage': _('Error wrong email or password.')},
                                safe=False)
        userData = UserData.objects.get(user=user)
        if userData.isOAuth == True:
            return JsonResponse({   'err': True,
                                'errMessage': _('Error wrong email or password.')},
                                safe=False)
        login(request, user)
        return JsonResponse({   'err': False,
                                'username': user.username,
                                'userData': serializers.serialize('json',[userData]) },
                                safe=False, status=200)
    elif request.method == 'GET':
        if request.user.is_authenticated:
            userData = UserData.objects.filter(user=request.user)
            if userData:
                jsonUserData = serializers.serialize('json', userData)
                return JsonResponse({   'err': False,
                                        'username': request.user.username, 
                                        'userData': jsonUserData}, safe=False, status=200 )
            else:
                return JsonResponse({   'err': True,
                'errMessage': _('UserData is borked or database is offline, this is not supposed to happen.'),},
                safe=False)
        else:
            return JsonResponse({   'err': True,
                'errMessage': _('Error you are not logged in.')},
                safe=False)
    else:
        return JsonResponse({   'err': True,
            'errMessage': _('Error you must use the POST or GET method.')},
            safe=False)


def register_view(request):
    """
    Register via API, client must send: username, password1, password2 and email in a POST
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            logout(request)
        username = request.POST.get('username')
        if not username:
            return JsonResponse({   'err': True,
                'errMessage': _('Error please add an username.')}, safe=False )
        if username != re.sub(r"\s+", "", username, flags=re.UNICODE):
            return JsonResponse({   'err': True,
                'errMessage': _('Error the username can\'t contain whitespaces.')}, safe=False )
        if len(username) > 30:
            return JsonResponse({   'err': True,
                'errMessage': _('Error the username is too long. The maximum length is 30 characters.')}, safe=False )

        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return JsonResponse({   'err': True,
                'errMessage': _('Error passwords diff.')}, safe=False )
        try:
            password_validation.validate_password(password1)
        except ValidationError as e:
            return JsonResponse({
                'err': True,
                'errMessage': ' '.join(e.messages) }, safe=False)

        email = request.POST.get('email')
        try:
            validate_email(email)
        except ValidationError as e:
            return JsonResponse({   'err': True,
                'errMessage': f'{str(e)}'}, safe=False)
        isExisting = CustomUser.objects.filter(email=email)
        if isExisting:
            return JsonResponse({   'err': True,
                'errMessage': _('Error this email is already taken.')}, safe=False)
        try:
            newUser = CustomUser.objects.create_user(username=username,
                                               email=email,
                                               password=request.POST.get('password1'))
            newUser.save()
            try:
                userData = UserData.objects.get(user=newUser)
                if uploadErr := updateProfilePicture(request, userData):
                    newUser.delete()
                    return uploadErr
                login(request, newUser)
                return JsonResponse({'err': False,
                        'username': newUser.username,
                        'userData': serializers.serialize('json', [userData]) }, safe=False)
            except:
                return JsonResponse({ 'err': True,
                        'errMessage': _('Error while creating new user.')}, safe=False)
        except ValueError as ve:
            return JsonResponse({   'err': True,
                'errMessage': f'{str(ve)}'}, safe=False)
    else:
        return JsonResponse({   'err': True,
            'errMessage': _('Error you must POST the register form.')}, safe=False)

def OAuth(request):
    """
    Register/Login through the 42 api.
    """
    retVal = HttpResponseRedirect(reverse('home'))
    if request.method != "GET":
        retVal['Location'] += _('?error=Error invalid request method.')
        return (retVal)
    if not request.GET.get('code'):
        retVal['Location'] += _('?error=Error you must be redirected by the 42 api.')
        return (retVal)
    code = request.GET.get('code')
    url = 'https://api.intra.42.fr/oauth/token'
    data = {'grant_type':'authorization_code',
            'client_id': os.getenv('API_UID'),
            'client_secret': os.getenv('API_SECRET'),
            'redirect_uri': os.getenv('API_REDIRECT_URI'),
            'code': code}
    response = requests.post(url, json=data)
    if response.status_code != 200:
        retVal['Location'] += _('?error=1Error while connecting to the 42 api.')
        return (retVal)
    jsonToken = json.loads(response.text)
    if not jsonToken["access_token"]:
        retVal['Location'] += _('?error=Error handshake with the 42 api failed.')
        return (retVal)
    header = {"Authorization": "Bearer " + jsonToken["access_token"]}
    response = requests.get("https://api.intra.42.fr/v2/me", headers=header)
    if response.status_code != 200:
        retVal['Location'] += _('?error=2Error while connecting to the 42 api.')
        return (retVal)
    UserInfos = json.loads(response.text)
    if not UserInfos["email"] or not UserInfos["login"]:
        retVal['Location'] += _('?error=Error while fetching infos from the 42 api.')
        return (retVal)
    email = UserInfos["email"]
    username = UserInfos["login"]
    user = CustomUser.objects.filter(email=email).first()
    if user is not None:
        if not loginOAuth(request, username, email, user):
            return JsonResponse({ 'err': True, 'errMessage': _('Error your email is already linked to another account without 42 OAuth.')}, safe=False)
    else:
        registerOAuth(request, username, email, UserInfos)
    return (retVal)


def logout_view(request):
    """
    Logout the user if possible
    """
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
            'errMessage': _('User in not logged.')},
            safe=False)
    logout(request)
    return JsonResponse({   'err': False,
            'errMessage': _('User successfully logged out.')},
            safe=False)

### USER PROFILE ###

def updateUserData(request):
    """
    Update UserData using API, client must send: 'language' in a POST.
    Client can optionaly send a file as 'profilePicture'.
    """
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must be logged in to modify your profile.')},
        safe=False)
    if not request.method == "POST":
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must use the POST method.')},
        safe=False)
    try:
        userData = UserData.objects.get(user=request.user)
        username = request.POST.get('username')

        if not username:
            return JsonResponse({   'err': True,
            'errMessage': _('Error please enter a valid username.')},
            safe=False )
        if username != re.sub(r"\s+", "", username, flags=re.UNICODE):
            return JsonResponse({   'err': True,
                        'errMessage': _('Error the username can\'t contain whitespaces.')},
                        safe=False )
        if len(username) > 30:
            return JsonResponse({   'err': True,
                'errMessage': _('Error the username is too long. The maximum length is 30 characters.')}, safe=False )

        request.user.username = username

        # Check and update password
        if not userData.isOAuth and (errPassword := checkAndSetPassword(request)):
            return errPassword

        # Update profile picture
        if uploadErr := updateProfilePicture(request, userData):
            return uploadErr

        request.user.save()
        return JsonResponse({'err': False,
                'username': request.user.username,
                'userData': serializers.serialize('json', [userData]) }, safe=False)
    except ValueError as ve:
            return JsonResponse({   'err': True,
                'errMessage': f'{str(ve)}'},
                safe=False)

def deleteUser(request):
    """
    Delete the user completely, username must be sent in a POST as 'usernameDelete'.
    """
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must be logged in to delete your profile lol.')},
        safe=False)
    if not request.method == "POST":
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must use the POST method.')},
        safe=False)
    try:
        username = request.POST.get('usernameDelete')
        if not username:
            return JsonResponse({   'err': True,
            'errMessage': _('Error please enter your username.')},
            safe=False )
        if username != request.user.username:
           return JsonResponse({   'err': True,
            'errMessage': _('Error wrong username.')},
            safe=False )
        if Tournament.objects.filter(models.Q(player_1=request.user)
                                    | models.Q(player_2=request.user)
                                    | models.Q(player_3=request.user)
                                    | models.Q(player_4=request.user)
                                    | models.Q(creator=request.user),
                                    status__in=['inProgress']).exists():
            return JsonResponse({   'err': True,
            'errMessage': _('Error cannot delete user involved in a tournament in-progress.')},
            safe=False )
        user = request.user
        user.delete()
    except Exception as e:
        return JsonResponse({   'err': True,
            'errMessage': _(f'Error while deleting the user please retry later. {e}')},
            safe=False )
    return JsonResponse({   'err': False,
            'errMessage': _('User successfully deleted. You will be redirected to the main page in 3 seconds.')},
            safe=False )

### FRIENDSHIP MANAGER ###

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

def sendFriendRequest(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must be logged in to send a friend request.')},
        safe=False)
    if not request.method == "POST":
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must use the POST method.')},
        safe=False)
    try:
        friendId = request.GET.get("friendId")
        if not friendId or not friendId.isnumeric():
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        newFriend = CustomUser.objects.get(id=int(friendId))
        if not newFriend:
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        if Friendship.objects.filter(
                (models.Q(friend_one=request.user, friend_two=newFriend)) |
                (models.Q(friend_one=newFriend, friend_two=request.user))).exists():
            return JsonResponse({   'err': True,
            'errMessage': _('Error you are already friend with this person.')},
            safe=False)
        if FriendRequest.objects.filter(sender=request.user, receiver=newFriend).exists():
            return JsonResponse({   'err': True,
            'errMessage': _('Error you already have sent a request to this person.')},
            safe=False)
        elif FriendRequest.objects.filter(sender=newFriend, receiver=request.user).exists():
            newFriendship = Friendship.objects.create(friend_one=request.user, friend_two=newFriend)
            newFriendship.save()
            friendrequest = FriendRequest.objects.filter(sender=newFriend, receiver=request.user)
            friendrequest.delete()
            return JsonResponse({   'err': False,
            'errMessage': _('Friend successfully added.')},
            safe=False)
        newRequest = FriendRequest.objects.create(sender=request.user, receiver=newFriend)
        newRequest.save()
        return JsonResponse({   'err': False,
            'errMessage': _('Friend request has been sent.')},
            safe=False)
    except:
        return JsonResponse({   'err': True,
            'errMessage': _('Error during friendship request, please retry later.')},
            safe=False)


def deleteFriendRequest(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must be logged in to send a friend request.')},
        safe=False)
    if not request.method == "POST":
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must use the POST method.')},
        safe=False)
    try:
        friendId = request.GET.get("friendId")
        if not friendId or not friendId.isnumeric():
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        friend = CustomUser.objects.get(id=int(friendId))
        if not friend:
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        friendRequest = FriendRequest.objects.filter(sender=request.user, receiver=friend)
        if not friendRequest:
            return JsonResponse({   'err': True,
            'errMessage': _('Error friend request not found.')},
            safe=False)
        friendRequest.delete()
        return JsonResponse({   'err': False,
            'errMessage': _('Friend request successfully deleted.')},
            safe=False)
    except:
        return JsonResponse({   'err': True,
            'errMessage': _('Error unable to remove the friend request please retry later.')},
            safe=False)
            


def deleteFriendship(request):
    if not request.user.is_authenticated:
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must be logged in to send a friend request.')},
        safe=False)
    if not request.method == "POST":
        return JsonResponse({   'err': True,
        'errMessage': _('Error you must use the POST method.')},
        safe=False)
    try:
        friendId = request.GET.get("friendId")
        if not friendId or not friendId.isnumeric():
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        oldFriend = CustomUser.objects.get(id=int(friendId))
        if not oldFriend:
            return JsonResponse({   'err': True,
            'errMessage': _('Error wrong user Id provided.')},
            safe=False)
        oldFriendship = Friendship.objects.filter(
                (models.Q(friend_one=request.user, friend_two=oldFriend)) |
                (models.Q(friend_one=oldFriend, friend_two=request.user)))
        if not oldFriendship:
            return JsonResponse({   'err': True,
            'errMessage': _('Error you are not friend with them.')},
            safe=False)
        oldFriendship.delete()
        return JsonResponse({   'err': False,
            'errMessage': _('Friendship successfully deleted.')},
            safe=False)
    except:
        return JsonResponse({   'err': True,
            'errMessage': _(f'Error unable to remove friendship please retry later. {e}')},
            safe=False)
