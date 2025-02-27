"""
Test script for the rieltor.ua scraper.
This script tests scraping a single URL and printing the results
without updating the database.
"""

import sys
import json
import traceback

from mysite.scrapers.rieltorua import RieltorScraper


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_scraper.py <property_url>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Testing scraper on URL: {url}")
    print("=" * 50)

    try:
        # Step 1: Initialize the scraper
        print("Step 1: Initializing scraper...")
        scraper = RieltorScraper(url)
        print(f"  Listing URL: {scraper.listing_url}")

        # Step 2: Scrape property details
        print("\nStep 2: Scraping property details...")
        property_details = scraper.scrape_property_details()

        if property_details:
            # Convert datetime objects to strings for JSON serialization
            for key, value in property_details.items():
                if hasattr(value, 'isoformat'):
                    property_details[key] = value.isoformat()

            print("\nExtracted property details:")
            print(json.dumps(property_details, indent=2, ensure_ascii=False))
            print("\nScraping successful! ✅")
        else:
            print("\nFailed to scrape property details - empty result returned.")
            print("Check the HTML structure or URL validity.")
    except Exception as e:
        print(f"\n❌ Error scraping URL: {e}")
        print("\nDetailed traceback:")
        print("-" * 50)
        traceback.print_exc()
        print("-" * 50)

        print("\nDebugging tips:")
        print("1. Check if the URL is accessible in your browser")
        print("2. Verify if the website structure has changed")
        print("3. Check your network connection")
        print("4. The site might be blocking scraping - consider adding delays")


if __name__ == "__main__":
    main()