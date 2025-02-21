from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
from typing import Optional

class WebScraper:

    def __init__(self, website_url:str, headers: dict = None, remove_tags=None, remove_styles=None):

        self.website_url = website_url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'
        }

        self.remove_tags = remove_tags or ["style"]
        self.remove_styles = remove_styles
        
    def get_page(self) -> Optional[requests.Response]:

        try:
            response = requests.get(self.website_url, headers=self.headers)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occcured: {err}")
            return None
        except Exception as err:
            print(f"Other error occcured: {err}")
            return None
    
    def clean_html(self, soup:BeautifulSoup) -> BeautifulSoup:

        """Clean up HTML by removing unnecessary tags or styles"""

        for tag in soup.find_all(self.remove_tags):
            tag.decompose()

        if self.remove_styles:
            for tag in soup.find_all(style=True):
                for style in self.remove_styles:
                    if style in tag["style"]:
                        del tag["style"]

        return soup
    
    def save_html(self, soup:BeautifulSoup, file_name: str) -> None:

        script_directory = os.path.dirname(os.path.abspath(__file__)) # the __file__ variable is a built-in Python variable that holds the path to the current script file.
        file_path = os.path.join(script_directory, 'scraped-html-pages', file_name)

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(soup.prettify())
        print(f"HTML saved in {file_name} file")

    def scrape(self) -> None:

        response = self.get_page()

        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            cleaned_soup = self.clean_html(soup)
        
            parsed_url = urlparse(self.website_url)
            site_name = parsed_url.netloc.replace('.', '-')
            file_name = f"{site_name}.html"

            self.save_html(cleaned_soup, file_name)
        else:
            print("Failed to retrieve the page")

scraper = WebScraper("https://dom.ria.com/uk/", remove_styles=["display:;"])
scraper.scrape()

