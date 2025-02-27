import re
import datetime
import mysql.connector
from typing import Dict, Optional, Tuple, List
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from mysite.scrapers.scraper import WebScraper
from mysite.service.databasehandler import DatabaseHandler


class RieltorScraper(WebScraper):
    """
    Specialized scraper for rieltor.ua property listings.
    Extracts property details and updates the database.
    """

    def __init__(self, listing_url: str):
        super().__init__(website_url=listing_url)
        self.listing_url = listing_url

    def scrape_property_details(self) -> Dict:
        """
        Scrapes the property details from the listing page.
        Returns a dictionary of property details.
        """
        response = self.get_page()
        if not response:
            return {}

        soup = BeautifulSoup(response.text, "html.parser")

        # Initialize property details dictionary
        property_details = {
            'url': self.listing_url,
            'source_website': 'rieltor.ua',
            'created_at': datetime.datetime.now(),
            'last_checked_at': datetime.datetime.now()
        }

        # Extract price
        price_elem = soup.select_one('.offer-view-price')
        if price_elem:
            # Extract digits from price string (removing currency and spaces)
            price_text = price_elem.text.strip()
            price_match = re.search(r'(\d[\d\s]*)', price_text)
            if price_match:
                price_str = price_match.group(1).replace(' ', '')
                try:
                    property_details['original_price'] = int(price_str)
                except ValueError:
                    property_details['original_price'] = 0

        # Extract description
        description_elem = soup.select_one('.offer-view-section-text')
        if description_elem:
            property_details['description'] = description_elem.text.strip()

        # Extract number of rooms
        # Look for room information in the characteristics section
            # Extract property details from the new structure
            detail_rows = soup.select('.offer-view-details-row')
            for row in detail_rows:
                # Get the text content of the span
                span = row.select_one('span')
                if not span:
                    continue

                text = span.text.strip()

                # Extract rooms information
                if 'кімнат' in text:
                    # Extract the number from "2 кімнати" or similar
                    rooms_match = re.search(r'(\d+)', text)
                    if rooms_match:
                        try:
                            property_details['number_of_rooms'] = int(rooms_match.group(1))
                        except ValueError:
                            pass

                # Extract floor information
                elif 'поверх' in text:
                    # Extract the floor from "поверх 2 з 5" or similar
                    floor_match = re.search(r'поверх\s+(\d+)', text)
                    if floor_match:
                        try:
                            property_details['floor'] = int(floor_match.group(1))
                        except ValueError:
                            pass

                # Extract area information - looking for pattern like "55 / 25 / 15 м²"
                elif 'м²' in text:
                    # Extract the first number (total area)
                    area_match = re.search(r'(\d+(?:\.\d+)?)', text)
                    if area_match:
                        try:
                            property_details['total_area'] = float(area_match.group(1))
                        except ValueError:
                            pass

        return property_details


def scrape_and_update_listing(url: str, db_config: Dict = None) -> bool:
    """
    Scrapes a property listing and updates the database.

    Args:
        url: The URL of the property listing
        db_config: Optional database configuration

    Returns:
        True if successful, False otherwise
    """
    try:
        # Initialize scraper and database handler
        scraper = RieltorScraper(url)
        db_handler = DatabaseHandler(**(db_config or {}))

        # Scrape property details
        property_details = scraper.scrape_property_details()
        if not property_details:
            db_handler.log_scraping_error(
                scraper.listing_id,
                f"Failed to scrape property details from {url}"
            )
            return False

        # Check if listing exists
        existing_listing = db_handler.listing_exists(scraper.listing_id)

        if existing_listing:
            # Update existing listing
            db_handler.update_listing(scraper.listing_id, property_details)

            # Check if price has changed
            if existing_listing['ORIGINAL_PRICE'] != property_details.get('original_price'):
                db_handler.add_price_history(
                    scraper.listing_id,
                    property_details.get('original_price')
                )
        else:
            # Insert new listing
            db_handler.insert_listing(property_details)

            # Add initial price history
            if 'original_price' in property_details:
                db_handler.add_price_history(
                    scraper.listing_id,
                    property_details['original_price']
                )

        # Update availability (assuming listing is available if we could scrape it)
        db_handler.update_availability(scraper.listing_id, True)

        return True
    except Exception as e:
        print(f"Error scraping and updating listing: {e}")
        # Try to log the error if possible
        try:
            listing_id = scraper.listing_id if 'scraper' in locals() else 0
            db_handler = DatabaseHandler(**(db_config or {}))
            db_handler.log_scraping_error(listing_id, str(e))
        except:
            pass
        return False