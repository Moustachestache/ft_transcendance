
import asyncio
import redis.asyncio as redis

from api.models import CustomUser, Match, Goal, Tournament, UserData
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

import logging
import time
from datetime import timedelta
from django.utils.translation import gettext as _
from .consumersUtils import sendMsgAndWait

logger = logging.getLogger('django')

WIDTH = 1280            # px
HEIGHT = 720            # px

GOALS_LIMIT = 9
MATCH_TIME_LIMIT = 120  # Sec

PADDLE_WIDTH = 15       # px
PADDLE_HEIGHT = 200     # px
PADDLE_SPEED = 600      # Pixels/Sec

BALL_SIZE = 15          # Radius in px
BALL_SPEED = 500        # Pixels/Sec

REFRESH_RATE = 1/30     # 30 times per seconds


"""All coordinates are calculated at the top left of every element
   It will be easier for the frontend ;) """

class Pong:

    class Player:
        def __init__(self, playerId, matchId):

            self.id = playerId
            self.userInstance = 0
            self.isConnected = False
            self.redisConn = f'match_user:{playerId}'
            self.inputRedisId = f'inputMatch:{matchId}:user:{playerId}'
            self.lastInput = '0-0'

            self.y = (HEIGHT / 2) - (PADDLE_HEIGHT / 2)
            self.direction = 0
            self.score = 0

    class Ball:
        def __init__(self):

            self.y = (HEIGHT / 2) - (BALL_SIZE / 2)
            self.x = (WIDTH / 2) - (BALL_SIZE / 2)
            self.xSpeed = BALL_SPEED
            self.ySpeed = BALL_SPEED

    def __init__(self, matchId, playerOneId, playerTwoId):

        """Communication"""

        self.channel_layer = get_channel_layer()
        self.channelLayerName = f'match_{matchId}'
        self.matchId = matchId

        """Game elements"""

        self.player1 = self.Player(playerOneId, matchId)
        self.player2 = self.Player(playerTwoId, matchId)
        self.ball = self.Ball()
        self.lastFrameTime = 0
        self.matchDuration = 0
        self.elapsedTime = 0
        self.winner = None

    async def getDbInstances(self):
        self.redis = await redis.from_url("redis://redis:6380", decode_responses=True)
        self.match = await database_sync_to_async(Match.objects.get)(id=self.matchId)
        self.player1.userInstance = await database_sync_to_async(CustomUser.objects.get)(id=self.player1.id)
        self.player2.userInstance = await database_sync_to_async(CustomUser.objects.get)(id=self.player2.id)
        if not self.match or not self.player1.userInstance or not self.player2.userInstance:
            self.error = True

    async def processInputs(self, player, signal):
        if signal == 'Start Up':
            player.direction = -1
        elif signal == 'Start Down':
            player.direction = 1
        elif signal == 'Stop Up' or signal == 'Stop Down':
            player.direction = 0
        else:
            logger.error(f'[gameLoop] Error wrong input received: "{signal}".')

    async def readInputs(self, player):
        messages = await self.redis.xread(streams={f'{player.inputRedisId}': f'{player.lastInput}'})
        for streamName, data in messages:
            for inputId, value in data:
                await self.processInputs(player, value['field'])
                player.lastInput = inputId

    async def checkPlayersConnection(self):
        isPlayer1 = await self.redis.get(self.player1.redisConn)
        isPlayer2 = await self.redis.get(self.player2.redisConn)
        if not isPlayer1:
            self.winner = self.player2.userInstance
            logger.info(f'[gameLoop] A player have disconnected, closing process.')
            return 1
        elif not isPlayer2:
            self.winner = self.player1.userInstance
            logger.info(f'[gameLoop] A player have disconnected, closing process.')
            return 1

    async def sendMatchInfos(self):
        await self.channel_layer.group_send( self.channelLayerName, {
        "type": "send.data",
        "signal": "matchData",
        "time": f"{int(self.elapsedTime // 60)}:{int(self.elapsedTime % 60):02}",
        "player1": {
            "id": self.player1.id,
            "y": self.player1.y
        },
        "player2": {
            "id": self.player2.id,
            "y": self.player2.y
        },
        "ball": {
            "x": self.ball.x,
            "y": self.ball.y,
        }, } )

    def createGoal(self, playerInstance, opponentInstance, time):
        logger.info(f'[gameLoop] Goal time: {time}')
        goal = Goal.objects.create( player=playerInstance, 
                                    opponent=opponentInstance,
                                    match=self.match,
                                    goalTime=time)
        goal.save()

    async def sendGoalInfos(self, playerInstance, opponentInstance):
        await database_sync_to_async(self.createGoal)(playerInstance, opponentInstance,timedelta(seconds=int(self.elapsedTime)))
        if self.player1.score >= GOALS_LIMIT or self.player2.score >= GOALS_LIMIT:
            self.inProgress = False
        await self.channel_layer.group_send( self.channelLayerName, {
            "type": "send.data",
            "signal": "scoreData",
            "player1": self.player1.score,
            "player2": self.player2.score, } )

    def setWinner(self, isP1, isP2): # Make sure the winner is not null
        match = Match.objects.get(id=self.matchId)
        if not isP1 and not isP2:
            if random.randrange(0, 2): # rand between 1 and 0
                match.winner = match.player1
            else:
                match.winner = match.player2
        elif not isP1:
            match.winner = match.player2
        else:
            match.winner = match.player1
        match.save()

    async def waitForPlayers(self, timeout):
        seconds = 0
        redisP1 = f'match_user:{self.player1.id}'
        redisP2 = f'match_user:{self.player2.id}'
        while seconds < timeout:
            player1Conn = await self.redis.get(redisP1)
            player2Conn = await self.redis.get(redisP2)
            if player1Conn and player2Conn:
                logger.info(f'[gameLoop] Both players are connected starting game loop.')
                self.inProgress = True
                return 0
            logger.info(f'[gameLoop] Players are not ready yet waiting...')
            await asyncio.sleep(1)
            seconds += 1
        await database_sync_to_async(self.setWinner)(player1Conn, player2Conn)
        return 1

    async def moveBall(self, ball, deltaTime):
        ball.y += ball.ySpeed * deltaTime
        ball.x += ball.xSpeed * deltaTime
        if ball.y - (BALL_SIZE / 2) < 0:
            ball.y = (BALL_SIZE / 2)
            ball.ySpeed *= -1.05
        elif ball.y + (BALL_SIZE / 2) > HEIGHT:
            ball.y = HEIGHT - BALL_SIZE
            ball.ySpeed *= -1.05
        if ball.x - BALL_SIZE - PADDLE_WIDTH < 0:
            if ball.y + (BALL_SIZE / 2) >= self.player1.y and ball.y - (BALL_SIZE / 2) <= self.player1.y + PADDLE_HEIGHT:
                ball.x = PADDLE_WIDTH + BALL_SIZE
                
                relativeIntersectY = (ball.y - self.player1.y) - PADDLE_HEIGHT / 2
                normalized = relativeIntersectY / (PADDLE_HEIGHT / 2)
                bounceAngle = normalized * (BALL_SPEED * 0.75)
                ball.ySpeed = bounceAngle
                ball.xSpeed = abs(ball.xSpeed) * 1.1
            else:
                self.player2.score += 1
                await self.sendGoalInfos(self.player2.userInstance, self.player1.userInstance)
                ball.xSpeed = BALL_SPEED
                ball.ySpeed = BALL_SPEED
                ball.x = (WIDTH / 2)
                ball.y = (HEIGHT / 2)
        elif ball.x + BALL_SIZE + PADDLE_WIDTH > WIDTH:
            if ball.y + (BALL_SIZE / 2) >= self.player2.y and ball.y - (BALL_SIZE / 2) <= self.player2.y + PADDLE_HEIGHT:
                ball.x = WIDTH - PADDLE_WIDTH - BALL_SIZE

                relativeIntersectY = (ball.y - self.player2.y) - PADDLE_HEIGHT / 2
                normalized = relativeIntersectY / (PADDLE_HEIGHT / 2)
                bounceAngle = normalized * (BALL_SPEED * 0.75)
                ball.ySpeed = bounceAngle
                ball.xSpeed = -abs(ball.xSpeed) * 1.1
            else:
                self.player1.score += 1
                await self.sendGoalInfos(self.player1.userInstance, self.player2.userInstance)
                ball.xSpeed = -BALL_SPEED
                ball.ySpeed = BALL_SPEED
                ball.x = (WIDTH / 2)
                ball.y = (HEIGHT / 2)


    async def movePaddle(self, player, deltaTime):
        if player.direction == 1 and player.y < HEIGHT - PADDLE_HEIGHT:
            player.y += PADDLE_SPEED * deltaTime
            if player.y > HEIGHT - PADDLE_HEIGHT:
                player.y = HEIGHT - PADDLE_HEIGHT
        elif player.direction == -1 and player.y > 0:
            player.y -= PADDLE_SPEED * deltaTime
            if player.y < 0:
                player.y = 0

    async def gameRules(self, deltaTime):
        if self.elapsedTime > MATCH_TIME_LIMIT and self.player1.score != self.player2.score:
            self.inProgress = False
            return
        await self.movePaddle(self.player1, deltaTime)
        await self.movePaddle(self.player2, deltaTime)
        await self.moveBall(self.ball, deltaTime)

    def updateMatchDb(self):
        match = Match.objects.get(id=self.matchId)
        match.matchDuration = timedelta(seconds=int(self.elapsedTime))
        match.status = 'finished'
        if not self.winner:
            if self.player1.score > self.player2.score:
                self.winner = self.player1.userInstance
            else:
                self.winner = self.player2.userInstance
        match.winner = self.winner
        match.save()
        userdata = UserData.objects.get(user=match.winner)
        userdata.score += 1
        userdata.save()
        self.match = match # Avoid winner 'None', by updating the local model.

    async def gameLoop(self):
        self.lastFrameTime = time.time()
        while self.inProgress:
            current_time = time.time()
            deltaTime = current_time - self.lastFrameTime
            self.lastFrameTime = current_time
            self.elapsedTime += deltaTime

            if await self.checkPlayersConnection():
                self.inProgress = False
            await self.readInputs(self.player1)
            await self.readInputs(self.player2)
            await self.gameRules(deltaTime)
            await self.sendMatchInfos()
            await asyncio.sleep(REFRESH_RATE)
        await database_sync_to_async(self.updateMatchDb)()

async def startGame(matchId, playerOneId, playerTwoId):
    game = Pong(matchId, playerOneId, playerTwoId)
    await game.getDbInstances()
    if hasattr(game, 'error') and game.error is True:
        logger.info(f'[Match] Error match with id:{game.matchId} do not exist.')
        return
    if await game.waitForPlayers(30):
        await game.redis.delete(f'matchStarted:{game.matchId}')
        logger.info(f'[Match] Error timeout, missing players.')
        return
    await sendMsgAndWait(game.channelLayerName, {
                'type': 'send.data',
                'signal': 'msg',
                'msg': _(f'Match is starting get ready !'),}, 2)
    await game.gameLoop()
    logger.info(f'[Match] End of match, result: {game.player1.score}:{game.player2.score}.')
    await game.channel_layer.group_send( game.channelLayerName, {
        "type": "send.data",
        "signal": "gameEnd",
        "msg": f'{_('The winner is:')} {game.match.winner.username}' } )
    await game.redis.delete(f'matchStarted:{game.matchId}')
    await game.channel_layer.group_send( game.channelLayerName, {
        "type": "send.data",
        "signal": "quit",} )
