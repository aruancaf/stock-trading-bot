import sys
import flask
from flask import jsonify
import portfolio_manager
import stock_data_gatherer as sdg
import performance_metrics as pm

# Go to http://localhost:5000/portfolio to see active stock portfolio
app = flask.Flask(__name__)

def init_web():
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)
    sys.stdout.flush()

@app.route('/portfolio', methods=['GET'])
def display_stocks_web():
    portfolio = {
        "purchased": portfolio_manager.purchased,
        "sold": portfolio_manager.sold
    }
    return jsonify(portfolio)

@app.route('/portfolio/summary', methods=['GET'])
def portfolio_summary():
    summary = {
        "total_value": pm.calculate_total_value(portfolio_manager.purchased),
        "total_invested": pm.calculate_total_invested(portfolio_manager.purchased),
        "current_balance": pm.calculate_current_balance(portfolio_manager.purchased),
        "profit_loss": pm.calculate_profit_loss(portfolio_manager.purchased)
    }
    return jsonify(summary)

@app.route('/portfolio/details/<ticker>', methods=['GET'])
def stock_details(ticker):
    stock_info = sdg.get_current_stock_data(ticker)
    return jsonify(stock_info)

@app.route('/portfolio/history', methods=['GET'])
def transaction_history():
    history = portfolio_manager.get_transaction_history()
    return jsonify(history)

@app.route('/portfolio/metrics', methods=['GET'])
def performance_metrics():
    metrics = pm.calculate_performance_metrics(portfolio_manager.purchased)
    return jsonify(metrics)

@app.route('/portfolio/alerts', methods=['GET'])
def alerts():
    alerts = portfolio_manager.get_alerts()
    return jsonify(alerts)

if __name__ == "__main__":
    init_web()