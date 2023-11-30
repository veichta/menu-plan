import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.constants import MensaNames, MensaURL
from src.utils import cleanup_string, setup_driver


def get_uzh_menu(mensa: MensaNames):
    """Get menu for UZH Mensa

    Args:
        mensa (MensaNames): Mensa to get menu for

    Returns:
        list: List of dishes
    """
    logging.info(f"Getting menu for {mensa.value}...")
    url = MensaURL().get_url(mensa)
    logging.info(f"URL: {url}")

    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    section = soup.find("div", {"class": "NewsListItem--content"})

    # extract names
    elems = section.find_all("h3")
    elems = [name.get_text() for name in elems]
    elems = [name.split(" | ") for name in elems]
    elems = [(name[0].upper(), name[1].split(" / ")[0]) for name in elems if len(name) > 1]

    names = [cleanup_string(elem[0]) for elem in elems]
    prices = [float(cleanup_string(elem[1][4:])) for elem in elems]

    # extract dishes
    dishes = section.find_all("p")
    dishes = [dish.get_text() for dish in dishes]
    dishes = [
        cleanup_string(dish) for dish in dishes if not dish.startswith("Allergikerinformationen")
    ]
    dishes = dishes[1:]

    if len(names) != len(prices) or len(names) > len(dishes):
        raise ValueError("Length of names, prices and dishes must be equal")

    dishes = dishes[: len(names)]

    if not names:
        logging.info("No dishes found")
        names = ["No dishes available"]
        prices = [0.0]
        dishes = [""]

    for name, price, dish in zip(names, prices, dishes):
        logging.info(f"{name} - {price} - {dish}")

    return [(mensa.value, name, price, dish) for name, price, dish in zip(names, prices, dishes)]


def get_eth_menu(mensa: MensaNames):
    """Get menu for ETH Mensa

    Args:
        mensa (MensaNames): Mensa to get menu for

    Raises:
        ValueError: Mensa must be 'poly' or 'wok' or 'poly_abend'

    Returns:
        list: List of dishes
    """
    logging.info(f"Getting menu for {mensa.value}...")
    url = MensaURL().get_url(mensa)
    logging.info(f"URL: {url}")

    driver = setup_driver()
    driver.get(url)

    max_wait_time = 10
    # wait until #gastro-app has a section element
    try:
        # Wait for the presence of a section element inside #gastro-app
        section_inside_gastro_app_present = EC.presence_of_element_located(
            (By.CSS_SELECTOR, "#gastro-app section")
        )
        WebDriverWait(driver, max_wait_time).until(section_inside_gastro_app_present)
    except TimeoutException:
        logging.info("Timed out waiting for page to load")

    button_locator = "#gastro-app > div > section > div:nth-child(2) > div.cp-heading > div > button:nth-child(1)"
    button_to_click = WebDriverWait(driver, max_wait_time).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, button_locator))
    )
    button_to_click.click()

    source = driver.page_source

    soup = BeautifulSoup(source, "html.parser")

    main_section = "#gastro-app"
    main_section = soup.select(main_section)[0]
    main_section = main_section.select("section")[0]

    tables = list(main_section.children)
    if not len(tables):
        logging.info("No dishes found")
        return [(mensa.value, "No dishes available", 0.0, "")]

    if mensa in [MensaNames.poly, MensaNames.wok]:
        table = tables[1]
    elif mensa == MensaNames.poly_abend:
        table = tables[2]
    else:
        raise ValueError("Mensa must be 'poly' or 'wok' or 'poly_abend'")

    menus = list(
        table.select("div.cp-week.cp-week--wrap > section.cp-week__weekday > div.cp-week__days")
    )
    menus = list(menus[0].children)
    names = []
    prices = []
    dishes = []
    for menu in menus:
        ps = menu.findAll("p")
        logging.info(f"Found ps: {[ps.text for ps in ps]}")
        name = ps[0].text
        name = cleanup_string(name)

        dish = f"{menu.find('h3').text}| {ps[1].text}"
        dish = cleanup_string(dish)

        while ps[-1].text.startswith("+"):
            ps = ps[:-1]

        price = ps[-1].text.split("/")[0]
        price = float(cleanup_string(price))

        names.append(name)
        prices.append(price)
        dishes.append(dish)

    for name, price, dish in zip(names, prices, dishes):
        logging.info(f"{name} - {price} - {dish}")

    return [(mensa.value, name, price, dish) for name, price, dish in zip(names, prices, dishes)]


def get_menus():
    """Get all menus

    Returns:
        pd.DataFrame: Dataframe with all menus
    """

    menus = []
    for mensa in MensaNames:
        if mensa in [
            MensaNames.uzh_oben,
            MensaNames.uzh_unten,
            MensaNames.uzh_abend,
            MensaNames.platte,
        ]:
            menus += get_uzh_menu(mensa)
        elif mensa in [
            MensaNames.poly,
            MensaNames.poly_abend,
            MensaNames.wok,
        ]:
            menus += get_eth_menu(mensa)

    return pd.DataFrame(menus, columns=["mensa", "name", "price", "dish"])


if __name__ == "__main__":
    get_uzh_menu(MensaNames.uzh_oben)
    get_uzh_menu(MensaNames.uzh_unten)
    get_uzh_menu(MensaNames.uzh_abend)
    get_eth_menu(MensaNames.poly)
    get_eth_menu(MensaNames.poly_abend)
    get_eth_menu(MensaNames.wok)
