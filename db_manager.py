import psycopg2
from psycopg2.extras import RealDictCursor
import logging
import os

class dbHandler:
    def __init__(self, db_credentials):
            self.db_credentials = db_credentials
            self.connection = self.connect_to_db()
    def save_result(self, table_name, data):
        placeholders = ', '.join(['%s'] * len(data))
        columns = ', '.join(data.keys())
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        try:
            self.cursor.execute(sql, list(data.values()))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e

    def close(self):
        self.cursor.close()
        self.conn.close()        
    def connect_to_db(self):
        try:
            return psycopg2.connect(**self.db_credentials)
        except Exception as e:
            logging.error(f"Failed to connect to database: {e}")
            return None

    def insert_order(self, order_data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (ticker, order_type, quantity, price, order_status, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (order_data['ticker'], order_data['order_type'], order_data['quantity'], 
                  order_data['price'], order_data['order_status'], order_data['timestamp']))
            self.connection.commit()


    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except Exception as e:
            return self._extracted_from_execute_update_6(
                'Error executing query: ', e, None
            )

    def execute_update(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
            return True
        except Exception as e:
            return self._extracted_from_execute_update_6(
                'Error executing update: ', e, False
            )

    # TODO Rename this here and in `execute_query` and `execute_update`
    def _extracted_from_execute_update_6(self, arg0, e, arg2):
        logging.error(f"{arg0}{e}")
        self.connection.rollback()
        return arg2

    def close(self):
        self.cursor.close()
        self.connection.close()
        logging.info("Database connection closed.")

    # Methods to interact with the tables

    def insert_purchased_stock(self, ticker, purchase_price, quantity, purchase_date):
        query = """
        INSERT INTO purchased_stocks (ticker, purchase_price, quantity, purchase_date)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (ticker, purchase_date) DO NOTHING;
        """
        return self.execute_update(query, (ticker, purchase_price, quantity, purchase_date))

    def insert_sold_stock(self, ticker, sell_price, quantity, sell_date, purchase_date):
        query = """
        INSERT INTO sold_stocks (ticker, sell_price, quantity, sell_date, purchase_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ticker, sell_date) DO NOTHING;
        """
        return self.execute_update(query, (ticker, sell_price, quantity, sell_date, purchase_date))

    def insert_transaction(self, ticker, transaction_type, price, quantity, transaction_date):
        query = """
        INSERT INTO transactions (ticker, transaction_type, price, quantity, transaction_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (ticker, transaction_date) DO NOTHING;
        """
        return self.execute_update(query, (ticker, transaction_type, price, quantity, transaction_date))
    def insert_order(self, order_data):
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO orders (ticker, order_type, quantity, price, order_status, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (order_data['ticker'], order_data['order_type'], order_data['quantity'], 
                    order_data['price'], order_data['order_status'], order_data['timestamp']))
                self.connection.commit()

    def insert_position(self, position_data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO positions (ticker, quantity, average_price, current_price, profit_loss, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (position_data['ticker'], position_data['quantity'], position_data['average_price'],
                  position_data['current_price'], position_data['profit_loss'], position_data['timestamp']))
            self.connection.commit()

    def insert_backtest_result(self, result_data):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO backtest_results (strategy_name, ticker, start_date, end_date, initial_balance, final_balance, profit_loss, trades, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (result_data['strategy_name'], result_data['ticker'], result_data['start_date'],
                  result_data['end_date'], result_data['initial_balance'], result_data['final_balance'],
                  result_data['profit_loss'], result_data['trades'], result_data['timestamp']))
            self.connection.commi
    def fetch_purchased_stocks(self):
        query = "SELECT * FROM purchased_stocks;"
        return self.execute_query(query)

    def fetch_sold_stocks(self):
        query = "SELECT * FROM sold_stocks;"
        return self.execute_query(query)

    def fetch_transactions(self):
        query = "SELECT * FROM transactions;"
        return self.execute_query(query)

    def insert_stock_data(self, ticker, data, recorded_at):
        query = """
        INSERT INTO stock_data (ticker, data, recorded_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (ticker, recorded_at) DO NOTHING;
        """
        return self.execute_update(query, (ticker, data, recorded_at))

    def fetch_stock_data(self, ticker):
        query = "SELECT * FROM stock_data WHERE ticker = %s ORDER BY recorded_at DESC LIMIT 1;"
        return self.execute_query(query, (ticker,))
    
    def close(self):
        if self.connection:
            self.connection.close()