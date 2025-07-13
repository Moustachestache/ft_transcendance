from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserData, CustomUser
from django.contrib.auth.signals import user_logged_out
from django.utils import timezone
from datetime import timedelta


@receiver(post_save, sender=CustomUser)
def create_user_data(sender, instance, created, **kwargs):
    if created:
        UserData.objects.get_or_create(user=instance)


@receiver(user_logged_out)
def update_last_activity_on_logout(sender, request, user, **kwargs):
    if user.is_authenticated:
        user.last_activity = timezone.now() - timedelta(minutes=6) # so the check will be false in: is_user_online()
        user.save()

