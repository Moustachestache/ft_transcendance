
import json
import asyncio
import random

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer
from channels.db import database_sync_to_async
from api.models import CustomUser, Match, Goal, Tournament, UserData
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.crypto import get_random_string
from django.utils.translation import gettext as _
from .consumersUtils import sendMsgAndWait

from datetime import datetime, timezone, timedelta

import logging
logger = logging.getLogger('django')

class TournamentLoop:

    class   Player:
        def __init__(self, dbInstance):
            self.db = dbInstance
            self.redisConn = f'tournament_user:{self.db.id}'
            self.userChannel = f'user_{self.db.id}'

    def __init__(self, tournamentId):
        self.tournamentId = tournamentId
        self.tournamentChannel = f'tournament_{self.tournamentId}'
        self.tournamentStartedRedis = f'tournamentStarted:{self.tournamentId}'
        self.channel_layer = get_channel_layer()

        self.error = False
        self.inProgress = False
        self.final = None

    async def destructor(self):
        if await self.redis.get(self.tournamentStartedRedis):
            await self.redis.delete(self.tournamentStartedRedis)
        await self.channel_layer.group_send(self.tournamentChannel, {
            'type': 'send.data',
            'signal': 'disconnect', })


    async def waitForPlayers(self, timeout):
        seconds = 0
        playersConn = []
        while seconds < timeout:
            loggedUsers = 0
            playersConn.clear()
            for player in self.players:
                if await self.redis.get(player.redisConn):
                    loggedUsers += 1
            if loggedUsers == 4:
                logger.info(f'[tournamentLoop] All 4 players are connected. Starting Loop...')
                self.inProgress = True
                return
            await self.channel_layer.group_send(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'connected_players',
                'nbLoggedPlayers': f'{loggedUsers}',
                'nbMaxPlayers': f'{4}',
                'remainingTime': f'{timeout - seconds}', })
            await asyncio.sleep(1)
            seconds += 1

    def getTournamentAndPlayers(self):
        """This function is synchrone cause if not,
        django ORM do not return the players instances linked via foreign keys"""
        self.tournament = Tournament.objects.get(id=self.tournamentId)
        self.players = []
        self.players.append(self.Player(self.tournament.player_1))
        self.players.append(self.Player(self.tournament.player_2))
        self.players.append(self.Player(self.tournament.player_3))
        self.players.append(self.Player(self.tournament.player_4))
        for player in self.players:
            player.userData = UserData.objects.get(user=player.db)

    async def getDbInstances(self):
        self.redis = await redis.from_url("redis://redis:6380", decode_responses=True)
        try:
            await database_sync_to_async(self.getTournamentAndPlayers)()
        except:
            logger.error(f'[tournamentLoop] Error unable to get db instances for tournament id: {self.tournamentId}.')
            self.error = True

    def createMatch(self, player1, player2, winner=None):
        match = Match.objects.create(
            player_1=player1.db, 
            player_2=player2.db,
            tournament=self.tournament)
        if winner:
            match.winner = winner.db
        match.save()
        return match

    def updateMatch(self, matchId):
        self.tournament.status = 'closed'
        match = Match.objects.get(id=matchId)
        self.tournament.winner = match.winner
        self.tournament.save()
        return match

    async def startMatch(self, player1, player2): # Waiting 1 sec after the startMatch(), could not be enough my be: while not redis.get(matchredisconn)
        match = await database_sync_to_async(self.createMatch)(player1, player2)
        objToSend = {
            "type": "send.data",
            "signal": "match",
            "match_id": match.id,
            "player_1" : {  "id": player1.db.id,
                            "username": player1.db.username,
                            "profile_pic": str(player1.userData.profile_pic)},
            "player_2" : {  "id": player2.db.id, 
                            "username": player2.db.username,
                            "profile_pic": str(player2.userData.profile_pic)}
        }
        await self.channel_layer.group_send(player1.userChannel, objToSend)
        await self.channel_layer.group_send(player2.userChannel, objToSend)
        return match

    async def checkMatchs(self):
        matchsInProgress = 0
        match1StartedRedis = f'matchStarted:{self.matches[0].id}'
        match2StartedRedis = f'matchStarted:{self.matches[1].id}'
        if await self.redis.get(match1StartedRedis):
            matchsInProgress += 1
        if await self.redis.get(match2StartedRedis):
            matchsInProgress += 1
        if matchsInProgress == 0:
            return True
        await self.channel_layer.group_send(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'waiting_final',
                'matchsInProgress': matchsInProgress, })

    async def semiFinal(self):
        playersCopy = self.players
        random.shuffle(playersCopy)
        for player in self.players:
            if not await self.redis.get(player.redisConn):
                return None, None
        self.matches = []
        self.matches.append(await self.startMatch(playersCopy[0], playersCopy[1]))
        self.matches.append(await self.startMatch(playersCopy[2], playersCopy[3]))
        while self.inProgress:
            await asyncio.sleep(1)
            if await self.checkMatchs():
                self.inProgress = False
        self.matches[0] = await database_sync_to_async(self.updateMatch)(self.matches[0].id)
        self.matches[1] = await database_sync_to_async(self.updateMatch)(self.matches[1].id)
        winner1 = next(player for player in self.players if player.db.id == self.matches[0].winner.id)
        winner2 = next(player for player in self.players if player.db.id == self.matches[1].winner.id)
        return winner1, winner2

    async def finalMatch(self, winner1, winner2):
        isplayer1Connected = await self.redis.get(winner1.redisConn)
        isplayer2Connected = await self.redis.get(winner2.redisConn)
        if not isplayer1Connected and not isplayer2Connected:
            return
        elif not isplayer1Connected or not isplayer2Connected:
            winner = winner2 if not isplayer1Connected else winner1 
            self.final = await database_sync_to_async(self.createMatch)(winner1, winner2, winner)
            return
        self.final = await self.startMatch(winner1, winner2)
        self.inProgress = True
        while self.inProgress:
            await asyncio.sleep(1)
            if not await self.redis.get(f'matchStarted:{self.final.id}'):
                self.inProgress = False
        self.final = await database_sync_to_async(self.updateMatch)(self.final.id)

    async def loop(self):
        await sendMsgAndWait(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'Tournament is starting get ready !'),}, 2)
        
        winner1, winner2 = await self.semiFinal()

        if not winner1 or not winner2:
            await sendMsgAndWait(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'A player has left the tournament.') }, 2)
            return

        await sendMsgAndWait(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'The two finalists are: ') + f'{winner1.db.username}, {winner2.db.username}.',}, 2)

        logger.info(f'[Tournament] Final starting with : {winner1.db.username} vs {winner2.db.username}.')

        await self.finalMatch(winner1, winner2)

        if not self.final:
            await sendMsgAndWait(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'Too many players have left the tournament, no one have won.'),}, 2)
            return

        await sendMsgAndWait(self.tournamentChannel, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'The tournament winner is: ') + f'{self.final.winner.username}',}, 5)

        logger.info(f'[Tournament] The winner is: {self.final.winner.username}')


async def startTournament(tournamentId):
    logger.info(f'startTournament() has been triggered.')
    tournament = TournamentLoop(tournamentId)
    await tournament.getDbInstances()
    if hasattr(tournament, 'error') and tournament.error is True:
        await tournament.destructor()
        return
    await tournament.waitForPlayers(30)
    if tournament.inProgress:
        await tournament.loop()
    await tournament.destructor()
    logger.info(f'[tournamentLoop] End of tournament.')
