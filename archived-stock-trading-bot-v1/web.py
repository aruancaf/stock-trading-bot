import sys

import flask
from flask import jsonify

import portfolio_manager

# Go to http://localhost:5000/portfolio to see active stock portfolio
app = flask.Flask(__name__)


def init_web():
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)
    sys.stdout.flush()


@app.route('/portfolio', methods=['GET'])
def display_stocks_web():
    return jsonify({"purchased": portfolio_manager.purchased, "sold": portfolio_manager.sold})

