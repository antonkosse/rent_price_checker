# <ins> Purpose </ins>

The purpose of the repository is to create a python based web-scraper that would parse and store the selected by users rent offering
on periodic base. The idea would be to incorporate different parsers for different rent offering web-sites (like rieltor.ua, dim.ria etc)
and keep track of price changes for selected listings.

## <ins> Host </ins>
Hosting is done on pythonanywhere cloud solution, since the simplicity and rather small amount of data allow us to
use either free of basic account option

## <ins> Approximate database scheme </ins>

```mermaid
erDiagram
    listings {
        int id PK
        varchar(500) url UK
        varchar(255) title
        text description
        varchar(255) location
        int number_of_rooms
        decimal total_area
        int floor
        timestamp created_at
        timestamp last_checked_at
        int original_price
        varchar(100) source_website
    }
    
    title_image {
        int id PK
        int listing_id FK
        blob image
        timestamp created_at
    }

    price_history {
        int id PK
        int listing_id FK
        int price
        timestamp recorded_at
    }

    availability_history {
        int id PK
        int listing_id FK
        boolean is_available
        timestamp changed_at
    }

    user_watchlist {
        int id PK
        varchar(255) user_email
        int listing_id FK
        timestamp created_at
        boolean notify_on_price_change
        boolean notify_on_availability_change
    }

    scraping_errors {
        int id PK
        int listing_id FK
        text error_message
        timestamp occurred_at
    }

    listings ||--o{ price_history : "tracks_prices"
    listings ||--o{ availability_history : "tracks_availability"
    listings ||--o{ user_watchlist : "watched_by"
    listings ||--o{ scraping_errors : "has_errors"
    listings ||--|| title_image : "images"
```