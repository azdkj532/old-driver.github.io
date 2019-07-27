import os

from flask import Flask, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


CHARS62 = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def base62_encode(integer):
    integer = int(integer)
    seq = []
    while integer != 0:
        seq.append(CHARS62[integer % 62])
        integer //= 62
    seq.reverse()
    return ''.join(seq)


class Plurk(db.Model):
    __tablename__ = 'plurks'

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.Integer)
    author_avatar = db.Column(db.Integer)
    content = db.Column(db.String())

    def __init__(self, id, author, author_avatar,content):

        self.id = id
        self.author = author
        self.author_avatar = author_avatar
        self.content = content

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
            'avatar': f'https://avatars.plurk.com/{self.author}-medium.gif',
            'link': 'https://www.plurk.com/p/{}'.format(base62_encode(self.id)),
        }


@app.route('/')
def index():
    return render_template('index.html',
                           background=url_for('static',
                                              filename='background.png'))


@app.route('/go', defaults={'p': 0}, methods=['GET'])
def go(p):
    try:
        p = int(p)
    except Exception:
        p = 0

    result = Plurk.query.order_by(Plurk.id.desc()).paginate(
        page=p, per_page=50, error_out=False)
    return jsonify({'data': [row.serialize() for row in result.items]})


@app.errorhandler(404)
def error404(error):
    return '<h1>車速過快 翻車了</h1>'


if __name__ == '__main__':
    if os.environ.get('APP_LOCATION') == 'heroku':
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    else:
        app.run(host='localhost', port=8080, debug=True)
