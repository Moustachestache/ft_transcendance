from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from datetime import timedelta

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    last_activity = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Languages(models.TextChoices):
    FRENCH = 'fr', 'français'
    UKRAINIAN = 'uk', 'Українська'
    GEORGIAN = 'ka', 'ქართული'
    EGYPTIAN = 'egy', '𓍑𓃏𓏎𓂝𓉣'
    ENGLISH = 'en', 'English'

class   Tournament(models.Model):

    STATUS_CHOICES = [
        ('open', 'Open'),
        ('inProgress', 'In Progress'),
        ('closed', 'Closed') ]

    title = models.CharField(max_length = 124)
    player_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'player_one')
    player_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'player_two')
    player_3 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'player_tree')
    player_4 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'player_four')
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'creator')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    winner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True, related_name = 'winner')
    creation_date = models.DateTimeField(auto_now_add = True)

class   Match(models.Model):

    STATUS_CHOICES = [
        ('finished', 'Finished'),
        ('inProgress', 'In Progress'),]

    player_1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, related_name = 'player_1', null=True, blank=True)
    player_2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.SET_NULL, related_name = 'player_2', null=True, blank=True)
    end_date =  models.DateTimeField(auto_now_add = True)
    matchDuration = models.DurationField(default=timedelta(seconds=0))
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, blank=True, null=True)
    creation_date = models.DateTimeField(auto_now_add = True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='inProgress')
    winner = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)

class   Goal(models.Model):
    match = models.ForeignKey(Match, on_delete = models.CASCADE)
    player = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'player' )
    opponent = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name = 'opponent' )
    goalTime = models.DurationField(default=timedelta(seconds=0))
    creation_date = models.DateTimeField(auto_now_add = True)

class   UserData(models.Model):
    profile_pic = models.ImageField(upload_to='profile_pic/', default='')
    score = models.IntegerField(default = 0)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    isOAuth = models.BooleanField(default=False)
    creation_date = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.user.username

class   FriendRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'receiver')
    creation_date = models.DateTimeField(auto_now_add = True)

class   Friendship(models.Model):
    friend_one = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'friend_one')
    friend_two = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'friend_two')
    creation_date = models.DateTimeField(auto_now_add = True)

class   News(models.Model):
    title = models.CharField(max_length = 124)
    content = models.TextField(max_length = 6000)
    language = models.CharField(max_length=10, choices=Languages.choices, default=Languages.ENGLISH)
    user = models.CharField(max_length=100, default=_("anonymous"))
    creation_date = models.DateTimeField(auto_now_add = True)
