from datetime import datetime
import json
import unicodedata
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from sqlmodel import select
from app.dbmodels import Product


scrapers_registry = {}


def register_scraper_pair(website_name: str, crawl_first_page, crawl_next_pages):
    """Registers both scrape and process functions for a website."""
    scrapers_registry[website_name] = (crawl_first_page, crawl_next_pages)


def crawl_search_term_carrefour(
    keyword: str,
    driver: WebDriver,
    webdriver_timeout: int,
    db_session,
    timestamp: datetime,
) -> str | None:
    """
    Crawls the first page of Carrefour's search results for a given keyword, scrapes product data,
    saves it to the database, and returns the link to the next page if available.

    Args:
        keyword (str): The search keyword for products.
        driver (WebDriver): The Selenium WebDriver used for browsing the website.
        webdriver_timeout (int): Maximum wait time for page elements to load.
        db_session (Session): The database session used for saving products.
        timestamp (datetime): The timestamp indicating the last update time.

    Returns:
        str | None: The URL of the next page if available, otherwise `None`.
    """
    keyword = keyword.replace(" ", "%20")
    driver.get(f"https://www.carrefour.com.ar/{keyword}?")
    WebDriverWait(driver, webdriver_timeout).until(
        lambda e: e.find_element(By.CSS_SELECTOR, ".min-vh-100 > script")
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")

    json_string = soup.find(class_="min-vh-100").find("script").text
    element_list = json.loads(json_string)["itemListElement"]
    final_products = []
    for elem in element_list:
        product = elem["item"]
        final_products.append(
            {
                "name": normalize_str(product["name"]),
                "brand": normalize_str(product["brand"]["name"]),
                "image_url": product["image"],
                "description": normalize_str(product["description"]),
                "web_id": product["gtin"],
                "price": product["offers"]["highPrice"],
                "supermarket": "carrefour",
                "last_updated": timestamp,
            }
        )
    next_link = driver.find_elements(By.XPATH, """//link[@rel="next"]""")

    save_to_db(final_products, db_session)

    return next_link[0].get_attribute("href") if len(next_link) == 1 else None


def crawl_remaining_pages_carrefour(
    next_page: str,
    driver: WebDriver,
    webdriver_timeout: int,
    db_session,
    timestamp: datetime,
):
    """
    Crawls additional pages of Carrefour's product listings, scrapes product data,
    and saves it to the database.

    Args:
        next_page (str): The URL of the page to start scraping from.
        driver (WebDriver): The Selenium WebDriver used for navigating pages.
        webdriver_timeout (int): Maximum wait time for elements to load.
        db_session (Session): The database session used for saving products.
        timestamp (datetime): The timestamp for when data was last updated.

    Returns:
        None
    """
    driver.get(next_page)
    WebDriverWait(driver, webdriver_timeout).until(
        lambda e: e.find_element(By.CSS_SELECTOR, ".min-vh-100 > script")
    )
    final_products = []
    while True:
        try:
            soup = BeautifulSoup(driver.page_source, "html.parser")

            json_string = soup.find(class_="min-vh-100").find("script").text
            element_list = json.loads(json_string)["itemListElement"]

            for elem in element_list:
                product = elem["item"]
                final_products.append(
                    {
                        "name": normalize_str(product["name"]),
                        "brand": normalize_str(product["brand"]["name"]),
                        "image_url": product["image"],
                        "description": normalize_str(product["description"]),
                        "web_id": product["gtin"],
                        "price": product["offers"]["highPrice"],
                        "supermarket": "carrefour",
                        "last_updated": timestamp,
                    }
                )
            next_link = driver.find_element(
                By.XPATH, """//link[@rel="next"]"""
            ).get_attribute("href")

            if next_link is not None:
                save_to_db(final_products, db_session)
                final_products.clear()
                driver.get(next_link)
                WebDriverWait(driver, webdriver_timeout).until(
                    lambda e: e.find_element(By.CSS_SELECTOR, ".min-vh-100 > script")
                )
            else:
                save_to_db(final_products, db_session)
                final_products.clear()
                break
        except NoSuchElementException:
            save_to_db(final_products, db_session)
            final_products.clear()
            break


register_scraper_pair(
    "carrefour", crawl_search_term_carrefour, crawl_remaining_pages_carrefour
)


def save_to_db(product_list, db_session):
    """
    Saves or updates a list of products in the database.

    Args:
        product_list (List[dict]): A list of dictionaries containing product details.
        db_session (Session): The database session used to execute queries and commit
            changes.

    Returns:
        None
    """
    products = [Product(**product_data) for product_data in product_list]

    for product in products:
        # Check if the product already exists in the database
        existing_product = db_session.exec(
            select(Product).where(Product.name == product.name)
        ).first()

        if existing_product:
            existing_product.brand = product.brand
            existing_product.image_url = product.image_url
            existing_product.description = product.description
            existing_product.price = product.price
            existing_product.supermarket = product.supermarket
        else:
            db_session.add(product)

    db_session.commit()


def normalize_str(input: str) -> str:
    """
    Normalizes a string by removing accent marks and diacritical marks.

    Args:
        input (str): The input string to normalize.

    Returns:
        str: The normalized string with accent marks removed.

    Example:
        >>> normalize_str("café")
        'cafe'
    """
    return "".join(
        [
            c
            for c in unicodedata.normalize("NFKD", input)
            if not unicodedata.combining(c)
        ]
    )
