import sys
sys.path.insert(0, '/home/nasii/antonchik-project/rent_price_checker')
try:
    from mysite.scrapers.scraperParentClass import WebScraper
    print("Імпорт успішний!")
except ModuleNotFoundError as e:
    print("Помилка імпорту:", e)
