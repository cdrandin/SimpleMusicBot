import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import quote
from difflib import SequenceMatcher

# TODO: If I want to take this further need to better categorize data into objects
# NOTE: Just "really" works when looking for 1 song.

LOGGER = logging.getLogger(__file__)
YOUTUBE_LINK = 'https://www.youtube.com'
QUERY_LINK = '{}/results?search_query='.format(YOUTUBE_LINK)


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def parse_html(e):
    data = {}
    data['href'] = e.select('a.yt-uix-tile-link')[0]['href']
    data['title'] = e.select('a.yt-uix-tile-link')[0]['title']

    return data


def parse_html_chunk(chunk):
    return list(map(parse_html, chunk))


def fetch_youtube_query(query):
    '''
    returns dict
    keys:
     - reason : what happened, if empty it was successful
     - href : if successful it will have the watch link for the query
    '''
    data = {}
    data['reason'] = ''
    data['href'] = ''

    try:
        r = requests.get('{}{}'.format(QUERY_LINK, quote(query)), timeout=5)
    except requests.exceptions.RequestException as e:
        data['reason'] = 'Failed to fetch link for `{}`'.format(query)
        LOGGER.exception(e)

    if data['reason'] == '':
        soup = BeautifulSoup(r.content, 'html.parser')
        vchunk = soup.find_all('div', class_='yt-lockup-content')
        data_chunk = parse_html_chunk(vchunk[:3])

        # check for reliability
        for d in data_chunk:
            # NOTE: eh..
            # if 'official' in d['title'].lower():
            #     d['similarity'] = 1.0
            # else:
            d['similarity'] = similar(
                query.lower(), d['title'].replace('-', '').lower())

        sorted_data_chunks = sorted(data_chunk, key=lambda k: k[
                                    'similarity'], reverse=True)

        data['href'] = sorted_data_chunks[0]['href']

    return data


def youtube_link(watch):
    return u'{}{}'.format(YOUTUBE_LINK, watch)


def main():
    # d = fetch_youtube_query('Stars Bahwee - Flavors')
    d = fetch_youtube_query(
        'How You Love Me (Arston Remix) (feat. Bright Lights)')

    print (d)
    print (youtube_link(d['href']))

if __name__ == '__main__':
    main()
