import discord
import asyncio
import logging
import logging.config
import os
import sys
import yaml

from service.youtube import youtube_fetch

LOGGER = logging.getLogger(__file__)
LOGGER.setLevel(logging.DEBUG)

PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(PROJECT_DIR, 'logging_config.yaml')) as infile:
    D = yaml.load(infile)
    D.setdefault('version', 1)
    logging.config.dictConfig(D)


class SimpleMusicBot(discord.Client):

    @asyncio.coroutine
    def on_ready(self):
        LOGGER.info('Logged in as')
        LOGGER.info(self.user.name)
        LOGGER.info(self.user.id)
        LOGGER.info('------')

        self.bot_ch = self.get_botcommands_channel()
        self.once = False
        self.task = asyncio.Task(self.reset_once())
        self.loop = asyncio.get_event_loop()

    @asyncio.coroutine
    def on_message(self, message):
        if message.content.startswith('!smb_intro'):
            yield from self.how_to(message)

        elif message.content.startswith('!youtube'):
            LOGGER.info('youtube')
            if not self.once and not message.channel.name == 'botcommands':
                yield from self.not_in_botcommands_channel_message(message)
                return

            yield from self.handle_youtube_fetch(message)

    @asyncio.coroutine
    def reset_once(self):
        while True:
            self.once = False
            yield from asyncio.sleep(5)

    def get_botcommands_channel(self):
        bot_ch = None
        for ch in self.get_all_channels():
            if ch.name == 'botcommands':
                bot_ch = ch
                break

        return bot_ch

    @asyncio.coroutine
    def how_to(self, message):
        msg = \
            '''
            Simple Music Bot commands:
                commands only work in `botcommands` channel

                `<>` are parameters `[<>]` are optional parameters
                - `!smb_intro`: brings up this message
                - `!youtube`: fetch youtube link of query
                    ex) `!youtube <query> [<channel>]`
            '''
        return self.send_message(message.channel, msg)

    # NOTE: No sure if should be here or in the service __init__ scope.
    @asyncio.coroutine
    def handle_youtube_fetch(self, message):
        ch = message.channel_mentions[
            0] if message.channel_mentions else message.channel
        msg_list = message.content.split()

        query = ' '.join(msg_list[1:])
        query = query.replace('<#{}>'.format(ch.id), '')
        LOGGER.debug(query)

        res = youtube_fetch.fetch_youtube_query(query)
        LOGGER.info(res)

        if res['reason'] == '':
            return self.send_message(ch, youtube_fetch.youtube_link(res['href']))
        else:
            return self.send_message(message.channel, res['reason'])

    @asyncio.coroutine
    def not_in_botcommands_channel_message(self, message):
        self.once = True
        bot_ch = self.botcommands_channel()
        return self.send_message(message.channel, 'Please post only in {}.'.format(bot_ch.mention))


def main():
    smb = SimpleMusicBot()
    smb.run(sys.argv[1])


if __name__ == '__main__':
    main()
