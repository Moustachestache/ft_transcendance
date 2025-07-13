from django.shortcuts import render
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.shortcuts import get_object_or_404

from .models import Match, UserData
from .utils import getImageExtention

# Create your views here.
