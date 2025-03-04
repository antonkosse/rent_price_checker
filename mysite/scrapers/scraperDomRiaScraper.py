import re
import datetime
from typing import Dict, Optional
from bs4 import BeautifulSoup

from mysite.scrapers.scraperParentClass import WebScraper
from mysite.service.databasehandler import DatabaseHandler

class DomRiaScraper(WebScraper):

    def __init__(self, listing_url: str):
        super().__init__(website_url=listing_url)
        self.listing_url = listing_url

    
    def scrape_property_details(self) -> Dict:

        response = self.get_page()
        if not response:
            return {}
        

        soup = BeautifulSoup(response.text, "html.parser")
        
        property_details = {
            'url': self.listing_url,
            'source_website': 'dom.ria.com',
            'created_at': datetime.datetime.now(),
            'last_checked_at': datetime.datetime.now()
        }

        price_tag = soup.find("b", class_="size30")
        raw_price = price_tag.text.strip() if price_tag else None
        normalized_price = self.normalize_price(raw_price)

        if normalized_price is None:
            cleaned_price = "0"
        else:
            cleaned_price = re.sub(r'\D', '', normalized_price)

        try:
            property_details['original_price'] = int(cleaned_price)
        except ValueError:
            property_details['original_price'] = 0

        
        description_elem = soup.select_one("div#mainDescription")
        if description_elem:
            property_details['description'] = description_elem.text.strip()

        detail_rows = soup.select("ul.main-list li")
        for row in detail_rows:
            text = row.get_text(" ", strip=True)

            if "кімнат" in text:
                rooms_match = re.search(r'(\d+)', text)
                if rooms_match:
                    try:
                        property_details['number_of_rooms'] = int(rooms_match.group(1))
                    except ValueError:
                        pass
        
            if "поверх" in text:
                floor_match = re.search(r'(\d+)\s*поверх', text)
                if floor_match:
                    try:
                        property_details['floor'] = int(floor_match.group(1))
                    except ValueError:
                        pass
            
            if 'Загальна площа' in text:
                area_match = re.search(r'Загальна площа\s*(\d+(?:\.\d+)?)', text)
                if area_match:
                    try:
                        property_details['total_area'] = float(area_match.group(1))
                    except ValueError:
                        pass

        print(property_details)



if __name__ == '__main__':
    scraper1 = DomRiaScraper("https://dom.ria.com/uk/realty-dolgosrochnaya-arenda-kvartira-kiev-dvrz-alma-atinskaya-ulitsa-32739287.html")
    scraper1.scrape_property_details()

    # def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
    #     deleted_tag = soup.find("span", class_="size24 bold")
    #     if deleted_tag and "видалено" in deleted_tag.text.lower():
    #         availability = "deleted"
    #         normalized_price = None
    #     else:
    #         availability = "available"
    #         price_tag = soup.find("b", class_="size30")
    #         raw_price = price_tag.text.strip() if price_tag else None
    #         normalized_price = self.normalize_price(raw_price)
    #     return {
    #         "url": self.website_url,
    #         "price": normalized_price,
    #         "availability": availability
    #     }
