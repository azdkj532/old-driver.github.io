import os
import json
import argparse
from time import sleep
from urllib.parse import urlencode
import sys

import oauth2
import app

PLURK_APP_KEY = os.environ.get('PLURK_APP_KEY')
PLURK_APP_SECRET = os.environ.get('PLURK_APP_SECRET')
PLURK_TOKEN = os.environ.get('PLURK_TOKEN')
PLURK_SECRET = os.environ.get('PLURK_SECRET')
PLURK_SEARCH_QUERY = os.environ.get('PLURK_SEARCH_QUERY', 'FF')

consumer = oauth2.Consumer(PLURK_APP_KEY, PLURK_APP_SECRET)
token = oauth2.Token(PLURK_TOKEN, PLURK_SECRET)
client = oauth2.Client(consumer, token)

def emit_request(query, offset=0):
    apiUrl = 'https://www.plurk.com/APP/PlurkSearch/search'
    payload = {
        'query': query,
        'offset': int(offset),
        'time': 2019
    }
    resp, content = client.request(
        apiUrl,
        method='POST',
        body=urlencode(payload)
    )

    if resp.status == 200:
        return json.loads(content)
    else:
        print('Got response header: {}'.format(resp.status))
        return {
            'last_offset': -1,
            'plurks': []
        }


def convert(query, offset=0):
    data = emit_request(query, offset)
    def _convert(p):
        ret = {
            key: p[key] for key in ['content', 'owner_id', 'plurk_id', 'porn']
        }
        ret['avatar'] = data['users'].get(p['owner_id'])
        return ret
    return {
        'last_offset': int(data['last_offset']),
        'plurks': [ _convert(p) for p in data['plurks'] ]
    }


def search(query):
    offset = 0
    while 0 <= offset < 800:
        data = convert(query, offset)
        if len(data['plurks']) > 0:
            offset = data['last_offset']
            yield from data['plurks']
        else:
            return



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--max', default=10,
                        help='maximum result output')
    parser.add_argument('query', help='search query')
    args = parser.parse_args()

    query = args.query or PLURK_SEARCH_QUERY
    print(f'Get Query: {query}')

    for plurk in search(query):
        if not plurk['porn']:
            continue

        print(plurk['plurk_id'])
        try:
            app.db.session.add(
                app.Plurk(
                    id=plurk['plurk_id'],
                    author=plurk['owner_id'],
                    author_avatar=plurk['avatar'],
                    content=plurk['content']
                )
            )
            app.db.session.commit()
        except Exception:
            break
