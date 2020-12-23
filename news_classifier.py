# using nltk vader  built in lexicon classifier because generating dataset for classifier myself would take too long

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

sentiment_polarity_analyzer = SentimentIntensityAnalyzer() # add some other words like bullish/bearish, risen, etc

def sentiment_analyzer(sentence):
    ss = sentiment_polarity_analyzer.polarity_scores(sentence)
    for k in ss:
        print(k, ":", ss[k], end=" ")
    print()

