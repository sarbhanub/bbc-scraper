from nltk.sentiment import SentimentIntensityAnalyzer

def get_sentiment(content):
    sid = SentimentIntensityAnalyzer()
    raw_scores = sid.polarity_scores(content)
    scores = {key: round(value, 3) for key, value in raw_scores.items()} # round to 3 decimal places
    return scores