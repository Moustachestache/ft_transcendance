import sys
from PIL import Image, ImageOps
from django.http import JsonResponse

import random
from .models import Tournament, Match, CustomUser

from datetime import timedelta
from django.utils import timezone

### UTILS ###

def getImageExtention(type):
    if type and '/' in type:
        return type.split('/')[1]
    return None


def createSquareThumbnail(input_image_path, output_image_path, size=256):
    try:
        with Image.open(input_image_path) as img:
            img.thumbnail((size, size), Image.LANCZOS)
            img_with_border = ImageOps.fit(img, (size, size), method=Image.LANCZOS, centering=(0.5, 0.5))
            img_with_border.save(output_image_path)
            return 0
    except Exception as e:
        return e

def is_user_online(user):
    if not user.is_authenticated:
        return False
    return user.last_activity >= timezone.now() - timedelta(minutes=5)#<--- this can be changed 

def registerUser(request, tournament, slotNb):
    if slotNb < 1 or slotNb > 4:
        return JsonResponse({   'err': True,
            'errMessage': 'Error wrong slot value.'}, safe=False)
    for slot in [tournament.player_1, tournament.player_2, tournament.player_3, tournament.player_4]: # make sure the user in not already registered
        if slot == request.user:
            return JsonResponse({   'err': True,
                'errMessage': 'Error you are already registered in this tournament.'}, safe=False)
    slot_field = f'player_{slotNb}'
    if getattr(tournament, slot_field):
        return JsonResponse({ 'err': True,
            'errMessage': 'Error: slot already taken.' }, safe=False)
    setattr(tournament, slot_field, request.user)
    tournament.save()
    return JsonResponse({ 'err': False,
            'errMessage': 'User successfully registered.' }, safe=False)

def pairing(tournament_title):
    try:
        tournament = Tournament.objects.get(title=tournament_title)
    except Tournament.DoesNotExist:
        return None
    tournament_match = list(Match.objects.filter(tournament=tournament))

    winners = []
    loosers = []

    if tournament_match:
        # récuperer les gagnants et les perdants
        for match in tournament_match:
            winners.append(match.winner)
            if match.player_1 == match.winner:
                loosers.append(match.player_2)
            else:
                loosers.append(match.player_1)
        
        if len(winners) != 2 or len(loosers) != 2:
            return None
        tmp = [winners, loosers]
        return tmp
    else:
        players = [tournament.player_1, tournament.player_2, tournament.player_3, tournament.player_4]
        opponent = []
        for i in range(0, len(players), 2):
            opponent.append((players[i], players[i + 1]))
        return opponent
