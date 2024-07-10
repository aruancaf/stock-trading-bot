import sys
import flask
from flask import jsonify
import portfolio_manager
import stock_data_gatherer as sdg
import performance_metrics as pm

# Initialize the Flask application
app = flask.Flask(__name__)

def init_web():
    """Initialize and run the Flask web server."""
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)
    sys.stdout.flush()

@app.route('/portfolio', methods=['GET'])
def display_stocks_web():
    """Endpoint to display the current portfolio."""
    portfolio = {
        "purchased": portfolio_manager.purchased,
        "sold": portfolio_manager.sold
    }
    return jsonify(portfolio)

@app.route('/portfolio/summary', methods=['GET'])
def portfolio_summary():
    """Endpoint to display a summary of the portfolio."""
    summary = {
        "total_value": pm.calculate_total_value(portfolio_manager.purchased),
        "total_invested": pm.calculate_total_invested(portfolio_manager.purchased),
        "current_balance": pm.calculate_current_balance(portfolio_manager.purchased),
        "profit_loss": pm.calculate_profit_loss(portfolio_manager.purchased)
    }
    return jsonify(summary)

@app.route('/portfolio/details/<ticker>', methods=['GET'])
def stock_details(ticker):
    """Endpoint to get details of a specific stock in the portfolio."""
    stock_info = sdg.get_current_stock_data(ticker)
    return jsonify(stock_info)

@app.route('/portfolio/history', methods=['GET'])
def transaction_history():
    """Endpoint to get the transaction history of the portfolio."""
    history = portfolio_manager.get_transaction_history()
    return jsonify(history)

@app.route('/portfolio/metrics', methods=['GET'])
def performance_metrics():
    """Endpoint to get performance metrics of the portfolio."""
    metrics = pm.calculate_performance_metrics(portfolio_manager.purchased)
    return jsonify(metrics)

@app.route('/portfolio/alerts', methods=['GET'])
def alerts():
    """Endpoint to get alerts related to the portfolio."""
    alerts = portfolio_manager.get_alerts()
    return jsonify(alerts)

if __name__ == "__main__":
    init_web()