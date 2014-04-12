__author__ = 'rfaulk'

from flickipedia.config import settings
from flask import Flask

import os
from flask.ext.login import LoginManager


# Instantiate flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.__secret_key__
app.config['VERSION'] = settings.__version__

login_manager = LoginManager()
login_manager.init_app(app)

