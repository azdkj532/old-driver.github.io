import os
import json
from time import sleep

import oauth2
import app

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
        'offset': offset,
        'time': 2019
    }
    resp, content = client.request(
        apiUrl,
        method='POST',
        body='&'.join(f'{key}={val}' for key, val in payload.items()))

    if resp.status == 200:
        return json.loads(content)
    else:
        return []


def convert(query, offset=0):
    data = emit_request(query, offset)
    def _convert(p):
        ret = {
            key: p[key] for key in ['content', 'owner_id', 'plurk_id', 'porn']
        }
        ret['avatar'] = data['users'].get(p['owner_id'])
        return ret
    return {
        'last_offset': data['last_offset'],
        'plurks': [ _convert(p) for p in data['plurks'] ]
    }


def search(query):
    offset = 0
    while True:
        data = convert(query, offset)
        if len(data['plurks']) > 0:
            offset = data['last_offset']
            yield from data['plurks']

def run():
    counter = 0
    for plurk in search('FF'):
        if not plurk['porn']:
            continue
        else:
            counter += 1

        if counter > 200:
            break

        q = app.db.session.query(app.Plurk).filter(app.Plurk.id == plurk['plurk_id'])
        if app.db.session.query(q.exists()):
            continue

        app.db.session.add(
            app.Plurk(
                id=plurk['plurk_id'],
                author=plurk['owner_id'],
                author_avatar=plurk['avatar'],
                content=plurk['content']
            )
        )
        app.db.session.commit()


if __name__ == '__main__':
    run()
