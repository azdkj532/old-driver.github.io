import os
import json
import argparse
from time import sleep
from urllib.parse import urlencode
import sys

import oauth2
from app import db, Plurk

PLURK_APP_KEY = os.environ.get('PLURK_APP_KEY')
PLURK_APP_SECRET = os.environ.get('PLURK_APP_SECRET')
PLURK_TOKEN = os.environ.get('PLURK_TOKEN')
PLURK_SECRET = os.environ.get('PLURK_SECRET')

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
            'plurks': [],
            'users': {},
        }


def convert(query, offset=0):
    data = emit_request(query, offset)
    def _convert(p):
        try:
            ret = {
                key: p[key] for key in ['content', 'owner_id', 'plurk_id', 'porn']
            }
            user = data['users'].get(str(p['owner_id']))
            ret['avatar'] = user['avatar']
            ret['author'] = user['display_name']
            return ret
        except:
            pass
    return {
        'last_offset': int(data['last_offset']),
        'plurks': list(filter(None, (_convert(p) for p in data['plurks'] )))
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
    parser.add_argument('--insert-only', default=False, const=True,
                        action='store_const',
                        help='stop when duplicate')
    args = parser.parse_args()

    print(f'Get Query: {args.query}')

    for plurk in search(args.query):
        if not plurk['porn']:
            continue

        try:
            instance = db.session.query(Plurk).filter(Plurk.id == plurk['plurk_id']).first()
            assert instance is not None

            if args.insert_only:
                break

            instance.author=plurk['owner_id'],
            instance.author_name=plurk['author'],
            instance.author_avatar=plurk['avatar'],
            instance.content=plurk['content']
        except Exception:
            db.session.add(
                Plurk(
                    id=plurk['plurk_id'],
                    author=plurk['owner_id'],
                    author_name=plurk['author'],
                    author_avatar=plurk['avatar'],
                    content=plurk['content']
                )
            )
        db.session.flush()
        db.session.commit()
