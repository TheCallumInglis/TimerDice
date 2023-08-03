from flask import Flask

webapp = Flask(__name__)

@webapp.route('/')
def index():
    return 'OK'