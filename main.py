import os
from src.loader import load_data
from src.mongoconnect import connect, close

def main(URI_SECRET):
    feeds = "feeds/rss.csv"
    client = connect(URI_SECRET)

    newsdb_prod = client["newsdb-prod"]
    sentdb_prod = client["sentdb-prod"]

    news_col = newsdb_prod['newscol']
    sent_col = sentdb_prod['sentcol']

    runtime = load_data(feeds=feeds,
                        news_col=news_col,
                        sent_col=sent_col)
    
    print(runtime)
    close(client)

if __name__ == "__main__":
    try:
        URI_SECRET = os.environ["URI_SECRET"]
        main(URI_SECRET)
    except KeyError:
        print("Invalid token")