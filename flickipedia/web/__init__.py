__author__ = 'rfaulk'

from flickipedia.config import settings
from flask import Flask

# Instantiate flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.__secret_key__
app.config['VERSION'] = settings.__version__
