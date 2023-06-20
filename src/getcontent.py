import requests
from bs4 import BeautifulSoup

def get_content(url):
    """
    Retrieves the content and image URL from a given webpage URL.

    Args:
        url (str): The URL of the webpage.

    Returns:
        tuple: A tuple containing the extracted content and image URL.
               If extraction fails, returns (None, None).
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        meta_tag = soup.find('meta', attrs={'property': 'og:image'})
        if meta_tag:
            image_url = meta_tag.get('content')
            if image_url and requests.head(image_url).status_code == 200:
                start_marker = '<article'
                end_marker = '</article>'
                start_index = response.text.find(start_marker)
                end_index = response.text.find(end_marker, start_index) + len(end_marker)
                article_html = response.text[start_index:end_index]
                soup = BeautifulSoup(article_html, 'html.parser')
                content = soup.get_text(separator=' ')
                return content, image_url
            
    except requests.exceptions.RequestException:
        pass

    return None, None