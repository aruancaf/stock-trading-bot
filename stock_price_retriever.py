import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

nltk.download('vader_lexicon')
sentimentAnalyzer = SentimentIntensityAnalyzer()
print(sentimentAnalyzer.polarity_scores(
    text="That rank is mainly influenced by a short-term technical score of 85. AAPL's rank also includes a long-term technical score of 82. The fundamental score for AAPL is 44. In addition to the average rating from Wall Street analysts, AAPL stock has a mean target price of 313.172. This means analysts expect the stock to rise 11.38% over the next 12 months.Overall Score - 70"))
