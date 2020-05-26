# stock-trading-bot

Stock trading bot written in python that evaluates active stocks and buy/sells undervalued and up-trending stocks.

## How does it work?

This code for this bot can be broken into 3 different parts:

  1) Web scrapes active stocks from yahoo finance.
  2) Evaluates active stocks using different strategies such as EMA crossovers and resistance breakthroughs.
  3) Evaluates current stock portfolio by checking if stock price has dropped below EMA line or has seen a significant
     decrease from a day's high.
  4) Buys and sells paper(fake) stocks based on previous data. Stores purchased and sold stocks within ``` stock_portfolio.json ```
 
 That's it!

### Why create and use a stock-trading-bot

- Evaluates good opportunities faster than a human can by evaluating multiple stocks simultaneously.
- Takes the emotions out of the equation.
- No time commitment after the bot has been setup.
- It is fun lol :smile:

#### To do List

- Add more trading strategies to ensure better returns.
- Refine buy and selling time
- Add machine learning sentiment analysis such that the stock bot can act upon earning reports and positive/negative 
  news articles.
  
by Aditya Oberai