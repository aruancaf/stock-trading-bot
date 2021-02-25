# using nltk vader  built in lexicon classifier because generating dataset for classifier myself would take too long, might create custom dataset tho

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import constants

financial_word_classification = {"bullish": 1, "bearish": -1, "volatile": -0.3, "risen": 0.5, "fell": -0.5, "growth": 0.5, "rally": 0.5, "buy": 0.7, "sell":-0.7} #add other words

nltk.download('vader_lexicon')
sentiment_polarity_analyzer = SentimentIntensityAnalyzer()

sentiment_polarity_analyzer.lexicon.update(financial_word_classification)

def sentiment_analyzer(sentences):
    summation = 0
    number_of_neutral = 0
    for sentence in sentences:
        sentence_score = sentiment_polarity_analyzer.polarity_scores(sentence)['compound']
        summation += sentence_score
        # print(sentence)
        # print("Score:", sentence_score, "\n\n\n\n")
        if sentence_score == 0:
            number_of_neutral += 1
    if len(sentences) >= constants.ARTICLE_MIN_COUNT_NEWS:
        return summation/(len(sentences)- number_of_neutral/2)
    return 0

