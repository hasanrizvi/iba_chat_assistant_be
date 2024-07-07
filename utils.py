import re
import requests
import html2text
from bs4 import BeautifulSoup, Comment

# Data Cleaning functions

def merge_hyphenated_words(text):
    return re.sub(r"(\w)-\n(\w)", r"\1\2", text)


def fix_newlines(text):
    return re.sub(r"(?<!\n)\n(?!\n)", " ", text)


def remove_multiple_newlines(text):
    return re.sub(r"\n{2,}", "\n", text)


def clean_text(text):
    cleaning_functions = [merge_hyphenated_words, fix_newlines, remove_multiple_newlines]
    for cleaning_function in cleaning_functions:
        text = cleaning_function(text)
    return text

def get_data_from_website(url):
    # Get response from the server
    response = requests.get(url)
    if response.status_code == 500:
        print("Server error")
        return

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Removing js and css code
    for script in soup(["script", "style", "noscript", "link"]):
        script.extract()

    header_div = soup.find("div", {"id": "header"})
    if header_div:
        header_div.extract()
    alert_div = soup.find("div", {"id": "alert"})
    if alert_div:
        alert_div.extract()
    subfooter_div = soup.find("div", {"class": "footer"})
    if subfooter_div:
        subfooter_div.extract()
    footer_div = soup.find("div", {"id": "footer"})
    if footer_div:
        footer_div.extract()
    top_button = soup.find("button", {"id": "myBtn"})
    if top_button:
        top_button.extract()

    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # Extract text in markdown format
    html = str(soup)
    html2text_instance = html2text.HTML2Text()
    html2text_instance.images_to_alt = True
    html2text_instance.body_width = 0
    html2text_instance.single_line_break = True
    text = html2text_instance.handle(html)

    # Extract page metadata
    try:
        page_title = soup.title.string.strip()
    except:
        page_title = url.path[1:].replace("/", "-")
    
    meta_description = soup.find("meta", attrs={"name": "description"})
    meta_keywords = soup.find("meta", attrs={"name": "keywords"})
    
    if meta_description:
        description = meta_description.get("content")
    else:
        description = page_title
    
    if meta_keywords:
        meta_keywords = meta_description.get("content")
    else:
        meta_keywords = ""

    metadata = {'title': page_title,
                'url': url,
                'description': description,
                'keywords': meta_keywords}

    return text, metadata