import discord
import asyncio
import logging
import logging.config
import os
import sys
import yaml

from service.youtube import youtube_fetch

ONCE = False
CLIENT = discord.Client()

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_DIR, 'logging_config.yaml')) as infile:
    D = yaml.load(infile)
    D.setdefault('version', 1)
    logging.config.dictConfig(D)


def how_to(message):
    s = \
        '''
    Simple Music Bot commands:
        commands only work in `botcommands` channel

        `<>` are parameters `[<>]` are optional parameters
        - `!smb_intro`: brings up this message
        - `!youtube`: fetch youtube link of query
            ex) `!youtube <query> [<channel>]`
    '''
    return CLIENT.send_message(message.channel, s)


def botcommands_channel():
    # HACK: lazy
    bot_ch = None
    for ch in CLIENT.get_all_channels():
        if ch.name == 'botcommands':
            bot_ch = ch
            break

    return bot_ch


def in_botcommands_channel(message):
    return message.channel.name == 'botcommands'


def not_in_botcommands_channel_message(message):
    ONCE = True
    bot_ch = botcommands_channel()
    return CLIENT.send_message(message.channel, 'Please post only in {}.'.format(bot_ch.mention))


@asyncio.coroutine
def reset_once():
    # HACK: lazy
    while True:
        global ONCE
        ONCE = False
        yield from asyncio.sleep(5)

task = asyncio.Task(reset_once())
loop = asyncio.get_event_loop()


def handle_youtube_fetch(message):
    ch = message.channel_mentions[
        0] if message.channel_mentions else message.channel
    msg_list = message.content.split()

    query = ' '.join(msg_list[1:])
    query = query.replace('<#{}>'.format(ch.id), '')
    LOGGER.debug(query)

    res = youtube_fetch.fetch_youtube_query(query)
    LOGGER.info(res)

    if res['reason'] == '':
        return CLIENT.send_message(ch, youtube_fetch.youtube_link(res['href']))
    else:
        return CLIENT.send_message(message.channel, res['reason'])


@CLIENT.event
async def on_ready():
    LOGGER.info('Logged in as')
    LOGGER.info(CLIENT.user.name)
    LOGGER.info(CLIENT.user.id)
    LOGGER.info('------')


@CLIENT.event
async def on_message(message):
    # HACK: lazy
    global ONCE

    if message.content.startswith('!smb_intro'):
        await how_to(message)

    elif message.content.startswith('!youtube'):
        LOGGER.info('youtube')
        if not ONCE and not in_botcommands_channel(message):
            await not_in_botcommands_channel_message(message)
            return

        await handle_youtube_fetch(message)

CLIENT.run(sys.argv[1])
