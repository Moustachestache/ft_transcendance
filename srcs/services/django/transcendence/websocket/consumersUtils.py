import asyncio

from channels.layers import get_channel_layer

import logging
logger = logging.getLogger('django')


async def sendMsgAndWait(channel, dictToSend, timeout):
    """Send the dictionary to the django channel, and wait for timout seconds"""
    try:
        int(timeout)
        str(channel)
        dict(dictToSend)
        channel_layer = get_channel_layer()
        await channel_layer.group_send(channel, dictToSend)
        await asyncio.sleep(timeout)
    except:
        logger.info(f'[sendMsgAndWait] Wrong data type sent')
