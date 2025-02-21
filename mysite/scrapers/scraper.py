from bs4 import BeautifulSoup
import requests
import os
from urllib.parse import urlparse

def html_page_scraping(website_url:str) -> None:
    url = website_url
    headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0'
        }
    page = requests.get(url, headers=headers)

    parsed_url = urlparse(url)
    site_name = parsed_url.netloc 

    site_name = site_name.replace('.', '-')

    file_name = f"{site_name}.html"


    script_directory = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_directory, file_name)

    if page.status_code == 200:
        print(f"Success. Status code: {page.status_code}")

        html_content = page.text

        soup = BeautifulSoup(page.text, "html.parser")
        for tag in soup.find_all(style=True):
            if "display:;" in tag["style"]:
                del tag["style"]


        with open(file_path, "w", encoding="utf-8") as file:
            file.write(soup.prettify())

        print(f"HTML saved in {file_name} file")


    else:
        print(f"Error. Status code: {page.status_code}")
