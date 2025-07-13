import json
import asyncio

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer
from channels.db import database_sync_to_async
from api.models import CustomUser, Match, Goal, Tournament, UserData
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.crypto import get_random_string

from datetime import datetime, timezone, timedelta

from .tournamentLoop import startTournament

import logging
logger = logging.getLogger('django')

class TournamentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            logger.info(f'[Tournament] Error user in not logged in.')
            await self.close()
            return
        logger.info(f'[Tournament] New incoming connection from user id: {self.scope['user'].id}.')
        if await self.duplicateSessionHandler():
            return

        await self.accept()
        self.connected = True
        await self.channel_layer.group_add(self.tournamentChannel, self.channel_name)
        await self.channel_layer.group_add(self.userChannel, self.channel_name)
        tournamentLock = await self.redis.set(self.tournamentLock, "1", nx=True, px=5000)
        if tournamentLock:
            loopStarted = await self.redis.get(self.tournamentStartedRedis)
            if not loopStarted:
                await self.redis.set(self.tournamentStartedRedis, self.channel_name)
                await self.redis.delete(self.tournamentLock)
                if await database_sync_to_async(self.isTournamentInProgress)():
                    logger.info(f'[Tournament] user id: {self.id} have started the tournament server.')
                    asyncio.create_task(startTournament(self.tournamentId))
                    return
                else:
                    logger.info(f'[Tournament] Error no tournament with id: {self.tournamentId}.')
                    await self.redis.delete(self.tournamentStartedRedis)
                    await self.close()
                    return

    async def disconnect(self, close_code):
        logger.info(f'[Tournament] Disconnect.')
        if hasattr(self, 'connected') and self.connected and hasattr(self, 'redis'):
            if await self.redis.get(self.redisConnId):
                await self.redis.delete(self.redisConnId)
            if await self.redis.get(self.redisLock):
                await self.redis.delete(self.redisLock)

    async def receive(self, text_data):
        logger.info(f'[Tournament] user id: {self.id} sent: {text_data}')

    async def send_data(self, event):
        if event['signal'] == 'disconnect':
            await self.close()
            return
        await self.send(text_data=json.dumps(event))

    def isTournamentInProgress(self):
        try:
            tournament = Tournament.objects.get(
                Q(player_1=self.user) | 
                Q(player_2=self.user) | 
                Q(player_3=self.user) | 
                Q(player_4=self.user),
                id=int(self.tournamentId),
                status='inProgress')
            if not tournament:
                return False
        except:
            return False
        return True

    async def initSelf(self):
        self.id = self.scope['user'].id
        self.user = self.scope["user"]
        self.username = self.scope["user"].username
        self.tournamentId = self.scope['url_route']['kwargs']['tournamentId']
        self.tournamentChannel = f'tournament_{self.tournamentId}'
        self.userChannel = f'user_{self.id}'
        self.redisConnId = f'tournament_user:{self.id}'
        self.redisLock = f'lock:{self.redisConnId}'
        self.tournamentLock = f'lock:tournament:{self.tournamentId}'
        self.tournamentStartedRedis = f'tournamentStarted:{self.tournamentId}'

    async def duplicateSessionHandler(self):
        """ This function is called upon connection, it avoid duplicated connections with the same client. """
        await self.initSelf()

        try:
            int(self.tournamentId)
        except:
            logger.info(f'[Tournament] tournamentId id Nan : {self.tournamentId}')
            return True

        self.redis = redis.from_url("redis://redis:6380", decode_responses=True)

        redisFree = await self.redis.set(self.redisLock, "1", nx=True, px=5000)
        if not redisFree:
            logger.info(f'[Tournament] Error user id: {self.id}, is already connected, and locking the redis.')
            await self.close()
            return True

        try:
            activeConsumer = await self.redis.get(self.redisConnId)
            if activeConsumer:
                logger.info(f"[Tournament] user id: {self.id} is already connected, closing connection...")
                await self.close()
                return True
            await self.redis.set(self.redisConnId, self.channel_name)
        finally:
            await self.redis.delete(self.redisLock)