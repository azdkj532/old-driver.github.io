import os

from bottle import route, run, static_file, error

@route('/')
@route('/static/<filename:path>')
def index(filename=None):
    if filename is None:
        filename = 'index.html'
    return static_file(filename, root='./static')

@error(404)
def error404(error):
    return '<h1>車速過快 翻車了</h1>'

if os.environ.get('APP_LOCATION') == 'heroku':
    run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
else:
    run(host='localhost', port=8080, debug=True)
