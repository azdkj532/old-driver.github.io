import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(
    name=__name__,
    static_url='/static',
    static_folder='./static'
)
db = SQLAlchemy(app)

@app.route('/', defaults={'path': 'index.html'})
@app.route('/static/<filename:path>')
def index(filename):
    return app.send_static_file(filename)


@app.route('/go')
def data(offset, db):
    try:
        offset = int(offset)
    except Exception:
        offset = 0
    row = db.execute('SELECT * FROM plurk LIMIT 50 OFFSET %s', (offset,))

    response.set_header('Content-Type', 'application/json')
    if row:
        return json.dumps(row)
    else:
        return []


@app.error(404)
def error404(error):
    return '<h1>車速過快 翻車了</h1>'

if os.environ.get('APP_LOCATION') == 'heroku':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    app.run(host='localhost', port=8080, debug=True)
