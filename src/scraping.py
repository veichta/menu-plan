import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

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

    if len(names) != len(prices) or len(names) != len(dishes):
        raise ValueError("Length of names, prices and dishes must be equal")

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
    soup = BeautifulSoup(driver.page_source, "html.parser")

    main_section = "contentMain"
    main_section = soup.find("section", {"id": main_section})

    tables = main_section.findAll("tbody")
    if mensa in [MensaNames.poly, MensaNames.wok]:
        table = tables[1]
    elif mensa == MensaNames.poly_abend:
        table = tables[3]
    else:
        raise ValueError("Mensa must be 'poly' or 'wok' or 'poly_abend'")

    rows = table.findAll("tr")
    names = []
    prices = []
    dishes = []
    for row in rows:
        cols = row.findAll("td")

        name = cols[0].get_text()
        name = cleanup_string(name)
        dish = str(cols[1]).split("<div")[0]
        dish = dish.replace("<td>", "").replace("<br/>", " ")
        dish = BeautifulSoup(dish, "html.parser").get_text()
        dish = cleanup_string(dish)
        price = cols[2].get_text()
        price = float(cleanup_string(price))

        names.append(name)
        prices.append(price)
        dishes.append(dish)

    driver.quit()

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
