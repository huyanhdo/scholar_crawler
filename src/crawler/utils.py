from pymongo import MongoClient
from dotenv import load_dotenv
import os
import re
import requests
from seleniumwire import webdriver

load_dotenv("src/crawler/.env.development")


def connect_to_mongodb():
    mongodb = MongoClient(host=os.getenv("MONGODB_HOST", "localhost:27018"))
    if os.getenv("DATABASE_USERNAME") is not None:
        mongodb.admin.authenticate(
            os.getenv("DATABASE_USERNAME"),
            os.getenv("DATABASE_PASSWORD"),
        )

    scholar_db = mongodb["scholar2"]
    return scholar_db


def request_get_with_scraper(url):
    # res = requests.get(
    #         "https://api.webscrapingapi.com/v1",
    #     params={"api_key": os.getenv("SCRAPER_API_KEY"), "url": url},
    # )
    res = requests.get(url)
    print(res.status_code)
    body = res.text
    return body


def is_linkedin_url(url):
    # must have suffix /in/ for profile url
    return re.match("https?://www.linkedin.com/in/.+", url)


def is_google_scholar_url(url):
    return re.match("http?s://scholar.google.com/citations.+", url) or re.match(
        "/citations\?", url
    )


def init_chromedriver_with_proxy():
    proxy_options = {
        "proxy": {
            "http": f'http://scraperapi:{os.getenv("SCRAPER_API_KEY")}@proxy-server.scraperapi.com:8001',
            "no_proxy": "localhost,127.0.0.1",
        }
    }
    chrome_options = webdriver.ChromeOptions()

    prefs = {"profile.managed_default_content_settings.images": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(
        executable_path="/home/datht/chromedriver",
        chrome_options=chrome_options,
        seleniumwire_options=proxy_options,
    )
    return driver
