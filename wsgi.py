#!/usr/bin/python3.7
from rndsite import app
from setproctitle import setproctitle

if __name__ == "__main__":
    setproctitle(f'{app.config["APP_NAME"]}')
    app.run(host='0.0.0.0', port=23045, debug=True)
