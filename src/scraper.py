import re
import requests
import datetime
import xml.etree.ElementTree as ET
from src.getcontent import get_content

bbc_format = "%a, %d %b %Y %H:%M:%S %Z"
id_format = "%Y%m%d"

def clean_text(content: str):
    content = content.lower()  # Convert to lowercase
    content = re.sub(r'(?<!\w)\.(?!\w)', ' ', content)  # Replace standalone periods with a space
    content = re.sub(r'(?<!\w)\.(?=\n)', '', content)  # Remove periods followed by a newline
    content = re.sub(r'\\', '', content)  # Remove backslashes
    content = re.sub(r'[^a-zA-Z0-9.,\'"\- ]', '', content)  # Remove invalid characters except for periods, commas, quotes, hyphens, and spaces
    content = re.sub(r'[\r\n]+', ' ', content)  # Replace consecutive newlines with a single space
    content = re.sub(r'\s+', ' ', content)  # Remove extra whitespaces
    return content.strip()

def scrape_feed(tag, rss_url, news_col):
    """
    Scrape articles from an RSS feed and update the tags field for existing articles.
    If an article with a given _id is not present in the database, a new article is added.

    Args:
        tag (str): The tag to associate with the articles.
        rss_url (str): The URL of the RSS feed to scrape.
        news_col: The MongoDB collection to store the articles.

    Returns:
        list: A list of dictionaries representing the scraped articles.
    """

    articles = []
    response = requests.get(rss_url)
    xml_content = response.content
    tree = ET.fromstring(xml_content)

    for item in tree.findall(".//item"):
        guid = item.find("guid").text
        try:
            _id = int(guid[-8:])
            existing = news_col.find_one({"_id": _id})

            if existing:
                if tag not in existing["tags"]:
                    existing_tags = existing["tags"]
                    modified_tags = existing_tags + ", " + tag
                    news_col.update_one({"_id": _id}, {"$set": {"tags": modified_tags}})

            else:
                title = item.find("title").text
                date_published = datetime.datetime.strptime(item.find("pubDate").text, bbc_format) 
                date_id = int(datetime.datetime.strftime(date_published, id_format))  # id format
                description_element = item.find("description")
                description = description_element.text if description_element is not None else ""
                raw_content, image_url = get_content(guid)
                content = clean_text(raw_content) if raw_content is not None else ""
                scraped_on = datetime.datetime.utcnow()

                articles.append({
                    "_id": _id,
                    "date_id": date_id,
                    "title": title,
                    "date_published": date_published,
                    "description": description,
                    "content": content,
                    "tags": tag,
                    "guid": guid,
                    "image_url": image_url,
                    "scraped_on": scraped_on
                })
    
        except ValueError:
            continue

    return articles