from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Match, Goal, UserData, News, CustomUser, Tournament, FriendRequest, Friendship


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    readonly_fields = ('date_joined',)
    exclude = ('last_name', 'first_name', 'date_joined')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        return form

# Register your models here.

class MatchAdmin(admin.ModelAdmin):
    list_display = ('player_1', 'player_2', 'winner', 'status', 'creation_date')
    search_fields = ('player_1', 'player_2', 'winner',)
    ordering = ('-creation_date',)
    fields = ('player_1', 'player_2', 'matchDuration', 'tournament', 'status', 'winner')

class   GoalAdmin(admin.ModelAdmin):
    list_display = ('player', 'opponent', 'match', 'creation_date')
    search_fields = ('player', 'opponent')
    ordering = ('-creation_date',)
    fields = ('match', 'player', 'opponent', 'goalTime',)

class   UserDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'score', 'profile_pic', 'isOAuth')
    search_fields = ('user', 'score')
    ordering = ('-score', '-creation_date',)
    fields = ('user', 'score', 'isOAuth')

class   NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'creation_date')
    search_fields = ('user', 'title')
    ordering = ('-creation_date',)
    fields = ('user', 'title', 'content', 'language')

class   TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'creation_date', 'status',)
    search_fields = ('title', 'creator')
    ordering = ('-creation_date',)
    fields = ('title', 'player_1', 'player_2', 'player_3', 'player_4', 'creator', 'status')

class   FriendRequestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver',)
    search_fields = ('sender', 'receiver',)
    ordering = ('-creation_date',)
    fields = ('sender', 'receiver',)

class   FriendshipAdmin(admin.ModelAdmin):
    list_display = ('friend_one', 'friend_two', )
    search_fields = ('friend_one', 'friend_two', )
    ordering = ('-creation_date',)
    fields = ('friend_one', 'friend_two', )

admin.site.register(UserData, UserDataAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(Goal, GoalAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(FriendRequest, FriendRequestAdmin)
admin.site.register(Friendship, FriendshipAdmin)
