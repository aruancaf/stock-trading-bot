import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import constants

# Financial word classification
financial_word_classification = {
    # Bullish words
    "bullish": 1.0, "rally": 0.7, "growth": 0.5, "buy": 0.7, "gain": 0.6,
    "surge": 0.8, "uptrend": 0.9, "strong": 0.6, "positive": 0.5, "optimistic": 0.7,
    
    # Neutral words
    "steady": 0.0, "neutral": 0.0, "flat": 0.0, "stable": 0.0, "unchanged": 0.0,
    "consistent": 0.0, "balanced": 0.0, "even": 0.0, "moderate": 0.0, "sideways": 0.0,
    
    # Earnings related words
    "earnings": 0.5, "profit": 0.7, "revenue": 0.6, "income": 0.5, "dividends": 0.6,
    
    # Bearish words
    "bearish": -1.0, "fell": -0.5, "sell": -0.7, "decline": -0.6, "drop": -0.7,
    "downtrend": -0.9, "weak": -0.6, "negative": -0.5, "pessimistic": -0.7, "loss": -0.8
}

# Download the required NLTK data
nltk.download('vader_lexicon')
nltk.download('punkt')
nltk.download('stopwords')

# Initialize the sentiment analyzer and update its lexicon
sentiment_polarity_analyzer = SentimentIntensityAnalyzer()
sentiment_polarity_analyzer.lexicon.update(financial_word_classification)

# Function to analyze sentiment
def sentiment_analyzer(sentences):
    summation = 0
    number_of_neutral = 0
    stop_words = set(stopwords.words('english'))
    
    for sentence in sentences:
        words = word_tokenize(sentence)
        filtered_sentence = ' '.join([word for word in words if word.lower() not in stop_words])
        sentence_score = sentiment_polarity_analyzer.polarity_scores(filtered_sentence)['compound']
        summation += sentence_score
        if sentence_score == 0:
            number_of_neutral += 1

    if len(sentences) >= constants.ARTICLE_MIN_COUNT_NEWS:
        return summation / (len(sentences) - number_of_neutral / 2)
    return 0

# Read the text file and process the sentences
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        sentences = file.readlines()
    return [sentence.strip() for sentence in sentences]

if __name__ == "__main__":
    # Path to the text file containing news articles
    file_path = 'news_articles.txt'
    
    # Read the text file
    sentences = read_text_file(file_path)
    
    # Analyze sentiment
    sentiment_score = sentiment_analyzer(sentences)
    print(f"Overall Sentiment Score: {sentiment_score}")