import time
from src.scraper import scrape_feed
from src.getsentiment import get_sentiment

def load_data(feeds, news_col, sent_col):
    """
    Loads and processes data from a list of feeds.

    Parameters:
        feeds (str): Path to the file containing the list of feeds.
        news_col: The collection where the news articles will be stored.
        sent_col: The collection where the sentiment scores will be stored.

    Returns:
        str: A string indicating the duration of the function execution in seconds
             and the total number of articles inserted, or a message indicating no articles to push.
    """
    start_time = time.time()
    total_articles = 0

    with open(feeds, "r") as file:
        lines = file.readlines()

    bulk_articles = []
    bulk_scores = []

    for line in lines:
        tag, url = line.strip().split(",")
        articles = scrape_feed(tag, url, news_col)
        
        if articles:
            for article in articles:
                if article["content"] != "":
                    score = get_sentiment(article["content"])
                elif article["description"] != "":
                    score = get_sentiment(article["description"])
                else:
                    score = get_sentiment(article["title"])

                score_data = {
                    "_id": article["_id"],
                    "date_id": article["date_id"],
                    "neg": score["neg"],
                    "neu": score["neu"],
                    "pos": score["pos"],
                    "compound": score["compound"]
                }
                
                bulk_scores.append(score_data)
                bulk_articles.append(article)

            if bulk_articles and bulk_scores:
                news_col.insert_many(bulk_articles)
                sent_col.insert_many(bulk_scores)
                total_articles += len(bulk_articles)
                bulk_articles = []
                bulk_scores = []

    execution_time = time.time() - start_time

    if total_articles > 0:
        return f"Pushed {total_articles} item(s); Job ran for {execution_time}s"
    else:
        return f"Nothing to push; Job ran for {execution_time}s"