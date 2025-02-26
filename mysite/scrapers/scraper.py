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
    
    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        raise NotImplementedError("Method extract_data() should be imlemented in child class")
    

    def scrape(self) -> None:

        response = self.get_page()

        if response:
            return self.extract_data(response)
        else:
            return {"url": self.website_url, "price": None, "availability": None}


class DomRiaScraper(WebScraper):
    None


class RieltorScraper(WebScraper):
    None

