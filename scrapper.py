from constants import URLS
import requests
import re
import os
import time
import logging
from utils import get_data_from_website, clean_text

def scrape_and_save(url):
    try:
        text, metadata = get_data_from_website(url)
        text = clean_text(text)

        # Create a directory to store scraped data if it doesn't exist
        if not os.path.exists('scraped_data'):
            os.makedirs('scraped_data')

        # Extract title from webpage and format it to snake case
        title = metadata['title']
        title_snake_case = re.sub(r'\W+', '_', title.lower()).strip('_')

        # Determine the filename
        base_filename = f'scraped_data/{title_snake_case}.txt'
        filename = base_filename

        # Check if the file already exists, if yes, append a number
        counter = 1
        while os.path.exists(filename):
            filename = f'{base_filename[:-4]}_{counter}.txt'  # Insert counter before the .txt extension
            counter += 1

        # Write extracted text to the determined filename
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)

        logging.info(f'Extracted text saved to {filename}')
        
    except requests.exceptions.RequestException as e:
        logging.error(f'Request failed for {url}: {e}')
    except Exception as ex:
        logging.error(f'Error processing {url}: {ex}')

if __name__ == "__main__":
    for url in URLS:
        scrape_and_save(url)
        time.sleep(10)