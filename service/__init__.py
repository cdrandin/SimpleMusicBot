from service.youtube import youtube_fetch
import asyncio
import logging

LOGGER = logging.getLogger(__file__)


# NOTE: Not sure how I feel about this yet. Just leaving for now.
@asyncio.coroutine
def handle_youtube_fetch(self, discord_message):
    ch = discord_message.channel_mentions[
        0] if discord_message.channel_mentions else discord_message.channel
    msg_list = discord_message.content.split()

    query = ' '.join(msg_list[1:])
    query = query.replace('<#{}>'.format(ch.id), '')
    LOGGER.debug(query)

    res = youtube_fetch.fetch_youtube_query(query)
    LOGGER.info(res)

    if res['reason'] == '':
        return self.send_discord_message(ch, youtube_fetch.youtube_link(res['href']))
    else:
        return self.send_discord_message(discord_message.channel, res['reason'])
