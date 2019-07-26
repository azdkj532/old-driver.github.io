import os

from flask import Flask, jsonify, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


class Plurk(db.Model):
    __tablename__ = 'plurks'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String())

    def __init__(self, content):

        self.content = content

    def serialize(self):
        return {
            'id': self.id,
            'content': self.content,
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
