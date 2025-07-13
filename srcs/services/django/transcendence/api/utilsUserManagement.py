from django.contrib.auth.models import User
from django.contrib.auth import login, logout, password_validation
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse

from .utils import getImageExtention, createSquareThumbnail
from .models import UserData, CustomUser

import requests, os

def updateProfilePicture(request, userData):
    profile_pic = request.FILES.get('profilePicture')
    if profile_pic:
        extension = getImageExtention(profile_pic.content_type)
        if extension not in ['png', 'jpeg', 'jpg', 'gif']:
            return JsonResponse({   'err': True,
                'errMessage': 'Error wrong file extension.'}, safe=False )
        userData.profile_pic.delete(save=False)#YESSSS#
        profile_pic.name = f'profile_id_{request.user.id}.{extension}'
        userData.profile_pic = profile_pic
        path = os.path.join(settings.MEDIA_ROOT + '/profile_pic/' + profile_pic.name)
        userData.save()
        createSquareThumbnail(path, path, 256)
    else:
        userData.save()
    return None

def checkAndSetPassword(request):
    password1 = request.POST.get('password1')
    password2 = request.POST.get('password2')
    if password1 or password2:
        if password1 != password2:
            return JsonResponse({   'err': True,
                'errMessage': 'Error passwords diff.'}, safe=False )
        try:
            password_validation.validate_password(password1)
            request.user.set_password(password1)
            login(request, request.user)
        except ValidationError as e:
            return JsonResponse({
                'err': True,
                'errMessage': ' '.join(e.messages)}, safe=False)
    return None

def registerOAuth(request, username, email, UserInfos):
    newUser = CustomUser.objects.create_user(username=username, email=email, password='')
    newUser.save()
    if request.user.is_authenticated:
        logout(request)
    login(request, newUser)
    userData = UserData.objects.get(user=newUser)
    try :
        fileUrl = UserInfos['image']['versions']['small']
        response = requests.get(fileUrl, stream=True)
        if response.status_code == 200:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(response.content)
            img_temp.flush()
            extension = fileUrl.split('.')[-1]
            img_filename = f'profile_id_{newUser.id}.{extension}'
            userData.profile_pic.save(img_filename, File(img_temp))
            profile_pic_path = os.path.join(settings.MEDIA_ROOT, 'profile_pic', img_filename)
            if not os.path.exists(os.path.dirname(profile_pic_path)):
                os.makedirs(os.path.dirname(profile_pic_path))
            os.rename(userData.profile_pic.path, profile_pic_path)
            userData.profile_pic.name = f'profile_pic/{img_filename}'
            userData.save()
            createSquareThumbnail(profile_pic_path, profile_pic_path, 256)
        else:
            userData.profile_pic.name = ''
    except:
        userData.profile_pic.name = ''
    userData.isOAuth = True
    userData.save()

def loginOAuth(request, username, email, user):
    userData = UserData.objects.get(user=user)
    if userData.isOAuth == True:
        if request.user.is_authenticated:
            logout(request)
        login(request, user)
        return 1
    return 0
