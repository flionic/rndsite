#!/usr/bin/env python3.7
import os

from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, instance_relative_config=True)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.url_map.strict_slashes = False
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['APP_NAME'] = 'rndsite'
app.config['APP_TITLE'] = 'Site Randomize'
app.config['VERSION'] = '0.0.1'
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', '7-DEV_MODE_KEY-7')
db_link = 'sqlite:///' + os.path.join(basedir, 'main.db')
app.config['SQLALCHEMY_DATABASE_URI'] = db_link
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.config['SESSION_TYPE'] = 'redis'
sess = Session(app)
login_manager = LoginManager(app)
login_manager.login_view = "users.login"


@login_manager.user_loader
def load_user(uid):
    return Settings.query.filter_by(key=uid).first()


@login_manager.unauthorized_handler
def unauthorized_handler():
    flash('Для этого действия требуется авторизация', 'error')
    return redirect(url_for('index'))


class Settings(db.Model):
    key = db.Column(db.String(24), primary_key=True, unique=True, nullable=False)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    @staticmethod
    def get_id():
        return 'username'

    def __repr__(self):
        return "'%s': '%s'" % (self.key, self.value)


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print('Start Flask')
    app.run(host=os.getenv('APP_IP', '0.0.0.0'), port=int(os.getenv('APP_PORT', 23045)), threaded=True, use_reloader=False, debug=True)
