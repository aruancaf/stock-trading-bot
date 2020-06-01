import sys

import flask
from flask import jsonify

import portfolio_manager
from utils import json_simplifier as json_simp

app = flask.Flask(__name__)


def init_web():
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='localhost', port=2000, debug=False, use_reloader=False)
    sys.stdout.flush()


@app.route('/purchased_portfolio', methods=['GET'])
def purchased_web():
    json_simp.read_json('purchased')
    return jsonify(portfolio_manager.purchased)


@app.route('/sold_portfolio', methods=['GET'])
def sold_web():
    json_simp.read_json('sold')
    return portfolio_manager.sold
