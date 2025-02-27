from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse
from typing import Dict, Optional

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

    
    def normalize_price(self, price: Optional[str]) -> Optional[str]:

        if not price:
            return {"amount": None, "currency": None}
        
        price = price.replace("\xa0", " ")
        currency = "грн" if "грн" in price else "$" if "$" in price else ""
        amount = re.sub(r"[^\d]", "", price)

        return f"{amount} {currency}".strip()
    

    def scrape(self) -> None:

        response = self.get_page()

        if response:
            soup = BeautifulSoup(response.text, "html.parser")
            return self.extract_data(soup)
        else:
            return {"url": self.website_url, "price": None, "availability": None}


class RieltorScraper(WebScraper):

    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:

        price_tag = soup.find("div",  class_="offer-view-price-title")
        price = price_tag.text.strip() if price_tag else None
        return {
            "url": self.website_url,
            "price": price
        }


class DomRiaScraper(WebScraper):

    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:

        price_tag = soup.find("b", class_="size30")
        raw_price = price_tag.text.strip() if price_tag else None
        normalized_price = self.normalize_price(raw_price)
        return {
            "url": self.website_url,
            "price": normalized_price
        }

scraper1 = DomRiaScraper("https://dom.ria.com/uk/realty-dolgosrochnaya-arenda-kvartira-kiev-mihaila-boychuka-ulitsa-30412680.html")
data1 = scraper1.scrape()
print(data1)

scraper2 = RieltorScraper("https://rieltor.ua/flats-rent/view/11739553/")
data2 = scraper2.scrape()
print(data2)