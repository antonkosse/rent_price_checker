from scraperParentClass import WebScraper

class DomRiaScraper(WebScraper):

    def extract_data(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        deleted_tag = soup.find("span", class_="size24 bold")
        if deleted_tag and "видалено" in deleted_tag.text.lower():
            availability = "deleted"
            normalized_price = None
        else:
            availability = "available"
            price_tag = soup.find("b", class_="size30")
            raw_price = price_tag.text.strip() if price_tag else None
            normalized_price = self.normalize_price(raw_price)
        return {
            "url": self.website_url,
            "price": normalized_price,
            "availability": availability
        }
