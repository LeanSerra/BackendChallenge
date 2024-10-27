import json
from typing import List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException


def crawl_search_term_carrefour(keyword: str, driver: WebDriver) -> List[dict]:
    keyword = keyword.replace(" ", "%20")
    driver.get(f"https://www.carrefour.com.ar/{keyword}?")
    WebDriverWait(driver, 15).until(
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
                        "name": product["name"],
                        "brand": product["brand"]["name"],
                        "image_url": product["image"],
                        "description": product["description"],
                        "id": product["mpn"],
                        "price": product["offers"]["highPrice"],
                    }
                )
            next_link = driver.find_element(
                By.XPATH, """//link[@rel="next"]"""
            ).get_attribute("href")

            if next_link is not None:
                driver.get(next_link)
                WebDriverWait(driver, 15).until(
                    lambda e: e.find_element(By.CSS_SELECTOR, ".min-vh-100 > script")
                )
            else:
                break
        except NoSuchElementException:
            break
    return final_products
