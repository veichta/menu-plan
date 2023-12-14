import json
import logging
import re

import pandas as pd


def cleanup_string(string):
    """Remove leading and trailing whitespace from a string.

    Args:
        string (str): The string to clean up.
    """
    return string.strip()


def clean_menu(string):
    """Remove leading and trailing whitespace from a string.

    Args:
        string (str): The string to clean up.
    """
    string = string.strip()
    string = string.replace("\n", " ")
    string = string.replace("\t", " ")
    string = string.replace("_", " ")
    string = string.replace("-", " ")
    string = string.replace("­", "")

    # remove multiple spaces
    string = re.sub(r"\s+", " ", string)

    # add whitespace after comma if missing
    string = re.sub(r",(\w)", r", \1", string)

    # remove everything after "Add on"
    string = re.sub(r"Add on.*", "", string)

    return string


def print_menu(mensa: str, menu: pd.DataFrame):
    """Print a menu in a nice format.

    Args:
        menu (pd.DataFrame): The menu to print.
    """
    emoji_mapping = json.load(open("data/mensa_emojis.json", "r"))

    mensa = clean_menu(mensa).upper()
    print(f"{mensa}\n{'-' * 20}")

    for _, row in menu.iterrows():
        name = clean_menu(row["name"]).title()

        emoji_name = name.lower().replace(" abend", "")
        logging.info(f"Emoji name: {emoji_name}")
        emoji = emoji_mapping.get(emoji_name, "💩")

        dish = clean_menu(row["dish"])

        price = row["price"]

        title = f"{name} (CHF {price:.2f})"
        print(f"{emoji} {title}: {dish}")

    print()
