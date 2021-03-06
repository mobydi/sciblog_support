import cherrypy
from paste.translogger import TransLogger
from flask import Flask, request, abort, jsonify, make_response, render_template
import json
import os
import pandas as pd
import lightgbm as lgb
from utils import BASELINE_MODEL, BAD_REQUEST, STATUS_OK, NOT_FOUND, SERVER_ERROR, PORT


# app
app = Flask(__name__)


@app.errorhandler(BAD_REQUEST)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request'}), BAD_REQUEST)


@app.errorhandler(NOT_FOUND)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), NOT_FOUND)


@app.errorhandler(SERVER_ERROR)
def server_error(error):
    return make_response(jsonify({'error': 'Server error'}), SERVER_ERROR)


@app.route('/')
def hello():
    return render_template('hello.html')


def manage_query(request):
    if not request.is_json:
        abort(BAD_REQUEST)
    dict_query = request.get_json()
    X = pd.DataFrame(dict_query, index=[0])
    X.to_csv('test.csv', index=False)
    return X


@app.route('/predict', methods=['POST'])
def predict():
    X = manage_query(request)
    y_pred = model.predict(X)[0]
    return make_response(jsonify({'fraud': y_pred}), STATUS_OK)


def run_server():
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'log.error_file': "cherrypy.log",
        'server.socket_port': PORT,
        'server.socket_host': '0.0.0.0',
        'server.thread_pool': 50, # 10 is default
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

# Load the model as a global variable
model = lgb.Booster(model_file=BASELINE_MODEL)    
    
    
if __name__ == "__main__":
    run_server()
    