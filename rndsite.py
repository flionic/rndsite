#!/usr/bin/env python3.7

import os
from werkzeug.contrib.fixers import ProxyFix
from flask import Flask, render_template

app = Flask(__name__, instance_relative_config=True)
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
app.wsgi_app = ProxyFix(app.wsgi_app)
app.config['APP_NAME'] = 'rndsite'
app.config['VERSION'] = '0.0.1'
app.config['SECRET_KEY'] = os.getenv('APP_SECRET_KEY', '7-DEV_MODE_KEY-7')


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print('Start Flask')
    app.run(host=os.getenv('APP_IP', '0.0.0.0'), port=int(os.getenv('APP_PORT', 23045)), threaded=True, use_reloader=False, debug=True)
