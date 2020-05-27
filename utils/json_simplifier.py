import json
import threading

import portfolio_manager

lock = threading.Lock()


def updated_purchased():
    with lock, open('purchased.json', "r+") as file:
        file.truncate(0)
        file.seek(0)
        json.dump(portfolio_manager.purchased, file, indent=4)


def updated_sold():
    with lock, open('sold.json', "r+") as file:
        file.truncate(0)
        file.seek(0)
        json.dump(portfolio_manager.sold, file, indent=4)


def read_json(f='all'):
    if f == 'all':
        with lock, open('purchased.json', "r+") as file:
            portfolio_manager.purchased = json.load(file)
        with lock, open('sold.json', "r+") as file:
            portfolio_manager.sold = json.load(file)
    elif f == 'purchased':
        with lock, open('purchased.json', "r+") as file:
            portfolio_manager.purchased = json.load(file)
    elif f == 'sold':
        with lock, open('sold.json', "r+") as file:
            portfolio_manager.sold = json.load(file)
    else:
        print('Invalid file name...')
