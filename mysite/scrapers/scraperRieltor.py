from scraperParentClass import WebScraper
from bs4 import BeautifulSoup
import requests
from typing import Dict, Optional

class RieltorScraper(WebScraper):

    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:

        deleted_block = soup.find("div", class_ = "offer-view-404")

        if deleted_block: 
            availability = "deleted"
            normalized_price = None
        else:
            availability = "available"
            price_tag = soup.find("div",  class_="offer-view-price-title")
            raw_price = price_tag.text.strip() if price_tag else None
            normalized_price = self.normalize_price(raw_price)
        return {
            "url": self.website_url,
            "price": normalized_price,
            "availability": availability
        }