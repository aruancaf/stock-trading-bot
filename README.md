# stock-trading-bot

Stock trading bot written in python that evaluates active stocks and buy/sells undervalued and up-trending stocks based on day trading patterns and news sentiment analysis.

## How does it work?

This code for this bot can be broken into 3 different parts:

1. Web scrapes active stocks from yahoo finance.
2. Evaluates active stocks (can evaluate 100s of stocks per minute as the application is multithreaded) using different strategies such as EMA crossovers/resistance breakthroughs, regression stock direction testing, and news sentiment analysis (buys and sells stocks based on quarterly earnings information or big news!).
3. Evaluates current stock portfolio by checking if any stock no longer seems worth holding.
4. Sends buy and sell requests using the alpaca paper trading api

That's it!

### Why create and use a stock-trading-bot

- Evaluates good opportunities faster than a human can by evaluating multiple stocks simultaneously.
- Takes the emotions out of the equation.
- No time commitment after the bot has been setup.
- It is fun lol :smile:

### How to use it

- Clone the repository: git clone https://github.com/aoberai/stock-trading-bot.git
- Install dependencies
  `pip3 install -r requirements.txt` for linux bash
  `py -m pip install -r requirements.txt` for windows command prompt
- Add a credentials.py file which has the information to your api keys / passwords
  1)Alpaca api for stock buying and selling handler + front end : https://alpaca.markets
  2)News API for stock sentiment analysis : https://newsapi.org

- Put the following 3 variables into your credentials.py file:

---

- ALP_API_ID=""
- ALP_SECRET_KEY=""
- NEWS_API_KEY=""

---

- Run the runner.py file!

### How to run in docker

```
docker build -t stock-trader-bot .
# you can change the timezone to be region specific
docker run --rm -it -e "TZ=America/New_York" -d -p 5000:5000 stock-trader-bot
```

Please create an issue if you are having problems getting the repo to work or if any part of the codebase look confusing -- I can help out.

#### To do List

- Add more trading strategies to ensure better returns.
- Refine buy and selling time
- Differentiate between long term and short term day trading positions

This repository is constantly getting better so please feel free to work with it and post pull requests if you encounter any bugs or want to add additional functionality. 

by Aditya Oberai
