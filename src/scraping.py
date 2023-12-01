import datetime
import json
import logging

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.constants import MensaNames, MensaURL
from src.utils import cleanup_string


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

    today = datetime.datetime.now()
    day_int = today.weekday()
    first_day = today - datetime.timedelta(days=today.weekday())
    last_day = first_day + datetime.timedelta(days=6)

    # Setup URL
    url = MensaURL().get_url(mensa)
    valif_after = first_day.strftime("%Y-%m-%d")
    valid_before = last_day.strftime("%Y-%m-%d")
    url = url.format(valif_after=valif_after, valid_before=valid_before)
    logging.info(f"URL: {url}")

    # Get response
    response = requests.get(url)
    response = json.loads(response.text.strip())

    # Find today's menu
    all_menus = response["weekly-rota-array"][0]["day-of-week-array"]
    menus = next(m for m in all_menus if m["day-of-week-code"] == day_int + 1)
    menus = menus["opening-hour-array"][0]["meal-time-array"]

    if mensa == MensaNames.poly_abend:
        menus = next(me for me in menus if me["name"] == "Abendessen")
    else:
        menus = next(me for me in menus if me["name"] == "Mittagessen")

    names = []
    prices = []
    dishes = []
    for menu in menus["line-array"]:
        name = menu["name"]
        if meal := menu.get("meal"):
            meal_name = meal["name"]
            desc = meal["description"]
            price = next(
                p["price"]
                for p in meal["meal-price-array"]
                if p["customer-group-desc"] == "Studierende"
            )
        else:
            meal_name = "Today's special is a surprise."
            desc = ""
            price = 0.0

        names.append(name)
        prices.append(price)
        dishes.append(f"{meal_name} | {desc}" if desc else meal_name)

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
