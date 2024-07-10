def calculate_total_value(purchased):
    return sum(stock['current_value'] for stock in purchased.values())

def calculate_total_invested(purchased):
    return sum(stock['purchase_price'] * stock['quantity'] for stock in purchased.values())

def calculate_current_balance(purchased):
    total_value = calculate_total_value(purchased)
    total_invested = calculate_total_invested(purchased)
    return total_value - total_invested

def calculate_profit_loss(purchased):
    total_value = calculate_total_value(purchased)
    total_invested = calculate_total_invested(purchased)
    return total_value - total_invested