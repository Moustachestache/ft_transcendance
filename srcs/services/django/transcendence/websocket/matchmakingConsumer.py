import json
import asyncio

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer
from channels.db import database_sync_to_async
from api.models import CustomUser, Match, Goal, Tournament, UserData
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.crypto import get_random_string

from datetime import datetime, timezone, timedelta

import logging
logger = logging.getLogger('django')


class Matchmaking(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            logger.info(f'[Matchmaking] Error user in not logged in.')
            await self.close()
            return
        logger.info(f'[Matchmaking] New incoming connection from user id: {self.scope['user'].id}.')
        if await self.duplicateSessionHandler():
            return

        await self.accept()
        self.connected = True
        await self.channel_layer.group_add(f'user_{self.id}', self.channel_name)

    async def disconnect(self, close_code):
        logger.info(f'[Matchmaking] Disconnect.')
        if hasattr(self, 'connected') and self.connected and hasattr(self, 'redis'):
            if await self.redis.get(self.redisConnId):
                await self.redis.delete(self.redisConnId)
            if await self.redis.get(self.redisLock):
                await self.redis.delete(self.redisLock)
            await self.redis.lrem("casual_queue", 0, self.id)

    async def receive(self, text_data):
        if text_data == 'enter_casual':
            await self.enterQueue('casual_queue')
        else:
            await self.disconnect()

    async def enterQueue(self, queueType):
        queueLocker = f'{queueType}Key'
        tries = 0
        while tries < 10:
            redisLock = await self.redis.set(queueLocker, "1", nx=True, px=5000)
            if redisLock:
                try:
                    await self.redis.rpush(queueType, self.id)
                    await self.matchmaking(queueType)
                finally:
                    await self.redis.delete(queueLocker)
                    return
            tries += 1
            await asyncio.sleep(1)
        await self.redis.rpush(queueType, self.id)

    def createMatch(self, player1Id, player2Id):
        player1 = CustomUser.objects.get(id=player1Id)
        UserDataP1 = UserData.objects.get(user=player1)
        player2 = CustomUser.objects.get(id=player2Id)
        UserDataP2 = UserData.objects.get(user=player2)
        newMatch = Match.objects.create(player_1=player1, player_2=player2)
        newMatch.save()
        return newMatch.id, player1, player2, UserDataP1, UserDataP2

    async def matchmaking(self, queueType):
        queueSize = await self.redis.llen(queueType)
        logger.info(f"[Matchmaking] user id:{self.id} entering matchmaking.")
        if queueSize < 2:
            return
        player1 = await self.redis.lpop(queueType)
        player2 = await self.redis.lpop(queueType)
        if player1 and player2:
            match_id, player1Db, player2Db, UserDataP1, UserDataP2 = await database_sync_to_async(self.createMatch)(player1, player2)
            objToSend = {
                "type": "send.match",
                "match_id": match_id,
                "player_1" : {  "id": player1Db.id,
                                "username": player1Db.username,
                                "profile_pic": str(UserDataP1.profile_pic)},
                "player_2" : {  "id": player2Db.id, 
                                "username": player2Db.username,
                                "profile_pic": str(UserDataP2.profile_pic) }}
            await self.channel_layer.group_send(
            f"user_{player2}", objToSend)
            await self.channel_layer.group_send(
            f"user_{player1}", objToSend)

    async def send_match(self, event):
        await self.send(text_data=json.dumps(event))

    async def initSelf(self):
        self.id = self.scope['user'].id
        self.username = self.scope["user"].username
        self.redisConnId = f'matchmaking_user:{self.id}'
        self.redisLock = f'lock:{self.redisConnId}'

    async def duplicateSessionHandler(self):
        """ This function is called upon connection, it avoid duplicated connections with the same client. """
        await self.initSelf()

        self.redis = redis.from_url("redis://redis:6380", decode_responses=True)

        redisFree = await self.redis.set(self.redisLock, "1", nx=True, px=5000)
        if not redisFree:
            logger.info(f'[Matchmaking] Error user id:{self.id}, is already connected, and locking the redis.')
            await self.close()
            return True

        try:
            activeConsumer = await self.redis.get(self.redisConnId)
            if activeConsumer:
                logger.info(f"[Matchmaking] user id:{self.id} is already connected, closing connection...")
                await self.close()
                return True
            await self.redis.set(self.redisConnId, self.channel_name)
        finally:
            await self.redis.delete(self.redisLock)

