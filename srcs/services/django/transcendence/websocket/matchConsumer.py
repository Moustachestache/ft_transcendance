import json
import asyncio

import redis.asyncio as redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels_redis.core import RedisChannelLayer
from channels.db import database_sync_to_async
from api.models import CustomUser, Match, Goal, Tournament
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils.crypto import get_random_string

from datetime import datetime, timezone, timedelta

from .gameLoop import startGame

import logging
logger = logging.getLogger('django')


class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            logger.info(f'[Match] Error user in not logged in.')
            await self.close()
            return
        logger.info(f'[Match] New incoming connection from user id:{self.scope['user'].id}.')
        if await self.duplicateSessionHandler():
            await self.close()
            return
        await self.accept()
        self.connected = True
        await self.send(text_data=json.dumps({"signal": "connected"}))
        await self.initSelf()

        await self.channel_layer.group_add(self.channelLayerName, self.channel_name)

        matchLock = await self.redis.set(self.matchLock, "1", nx=True, px=5000)
        if matchLock:
            loopStarted = await self.redis.get(self.matchStartedRedis)
            if not loopStarted:
                await self.redis.set(self.matchStartedRedis, self.channel_name)
                await self.redis.delete(self.matchLock)
                p1Id, p2Id = await self.get_match_player_ids(self.matchId)
                if p1Id and p2Id:
                    logger.info(f'[Match] user id:{self.id} have started the server.')
                    asyncio.create_task(startGame(self.matchId, p1Id, p2Id))
                    return
                else:
                    logger.info(f'[Match] Error no match with id:{self.matchId}.')

    async def disconnect(self, close_code):
        if hasattr(self, 'idle_task'):
            self.idle_task.cancel()
        await self.initSelf()
        logger.info(f'[Match] Disconnect.')
        if hasattr(self, 'connected') and self.connected and hasattr(self, 'redis'):
            if await self.redis.get(self.redisConnId):
                await self.redis.delete(self.redisConnId)
            if await self.redis.get(self.redisLock):
                await self.redis.delete(self.redisLock)
    
    async def receive(self, text_data):
        await self.initSelf()
        await self.handleGameInput(text_data)

    async def send_data(self, event):
        if event['signal'] and event['signal'] == 'quit':
            await self.close()
            return
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_match_player_ids(self, match_id):
        match = Match.objects.select_related("player_1", "player_2").get(id=match_id)
        return match.player_1.id, match.player_2.id

    async def handleGameInput(self, msg):
        await self.redis.xadd(self.inputRedisId, {"field": f"{msg}"})

    async def initSelf(self):
        self.id = self.scope['user'].id
        self.username = self.scope["user"].username
        self.redisConnId = f'match_user:{self.id}'
        self.redisLock = f'lock:{self.redisConnId}'
        self.matchId = self.scope['url_route']['kwargs']['matchId']
        self.inputRedisId = f'inputMatch:{self.matchId}:user:{self.id}'
        self.channelLayerName = f'match_{self.matchId}'
        self.matchLock = f'lock:match:{self.matchId}'
        self.matchStartedRedis = f'matchStarted:{self.matchId}'

    async def duplicateSessionHandler(self):
        """ This function is called upon connection, it avoid duplicated connections with the same client. """
        await self.initSelf()

        self.redis = redis.from_url("redis://redis:6380", decode_responses=True)

        redisFree = await self.redis.set(self.redisLock, "1", nx=True, px=5000)
        if not redisFree:
            logger.info(f'[Match] Error user id: {self.id}, is already connected, and locking the redis.')
            await self.close()
            return True

        try:
            activeConsumer = await self.redis.get(self.redisConnId)
            if activeConsumer:
                logger.info(f"[Match] user id: {self.id} is already connected, closing connection...")
                await self.close()
                return True
            await self.redis.set(self.redisConnId, self.channel_name)
        finally:
            await self.redis.delete(self.redisLock)

