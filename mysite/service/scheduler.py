import time
import schedule
import argparse
import datetime
import logging
from typing import List, Dict

from mysite.scrapers.rieltorua import scrape_and_update_listing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("rieltor_scraper")


def setup_db_config(args):
    """Create database configuration from command line arguments"""
    return {
        'host': args.db_host,
        'port': args.db_port,
        'user': args.db_user,
        'password': args.db_password,
        'database': args.db_name
    }


def scrape_listings(urls: List[str], db_config: Dict):
    """Scrape all listings in the list"""
    logger.info(f"Starting scraping of {len(urls)} listings at {datetime.datetime.now()}")

    success_count = 0
    for url in urls:
        try:
            logger.info(f"Scraping {url}")
            result = scrape_and_update_listing(url, db_config)
            if result:
                success_count += 1
            # Sleep between requests to avoid overloading the server
            time.sleep(2)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

    logger.info(f"Completed scraping. {success_count}/{len(urls)} successful.")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Rieltor.ua periodic scraper')
    parser.add_argument('--urls', nargs='+', required=True, help='URLs to scrape')
    parser.add_argument('--interval', type=int, default=12, help='Scraping interval in hours (default: 12)')
    parser.add_argument('--db-host', default='localhost', help='Database host (default: localhost)')
    parser.add_argument('--db-port', type=int, default=3306, help='Database port (default: 3306)')
    parser.add_argument('--db-user', default='user', help='Database user (default: user)')
    parser.add_argument('--db-password', default='password', help='Database password')
    parser.add_argument('--db-name', default='RC', help='Database name (default: RC)')

    args = parser.parse_args()

    db_config = setup_db_config(args)

    # Run immediately once
    scrape_listings(args.urls, db_config)

    # Schedule periodic runs
    schedule.every(args.interval).hours.do(scrape_listings, args.urls, db_config)

    logger.info(f"Scheduler set up to run every {args.interval} hours")

    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute for pending tasks


if __name__ == "__main__":
    main()