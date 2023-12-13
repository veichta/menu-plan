import argparse
import json
import logging

import numpy as np

from src.constants import MensaNames, MensaURL
from src.scraping import get_menus
from src.utils import print_menu
from src.weather import get_weather


def main(args):
    menu_df = get_menus()

    print_welcome_message(args)

    menu_per_mensa = menu_df.groupby("mensa")

    mensa_oder = [
        MensaNames.uzh_oben.value,
        MensaNames.uzh_unten.value,
        MensaNames.poly.value,
        MensaNames.wok.value,
        MensaNames.platte.value,
        MensaNames.uzh_abend.value,
        MensaNames.poly_abend.value,
    ]

    idx = 0
    for mensa_name in mensa_oder:
        if "abend" in mensa_name and args.time == "mittag":
            continue
        elif "abend" not in mensa_name and args.time == "abend":
            continue

        print_menu(f"{idx}: {mensa_name}", menu_per_mensa.get_group(mensa_name))
        idx += 1


def print_welcome_message(args):
    # with open("data/messages.json", "r") as f:
    #     messages = json.load(f)
    # greeting_msg = np.random.choice(messages["welcome-messages"])
    # print(f"{greeting_msg} Today is {MensaURL().weekday} and here is today's menu:\n")

    if MensaURL().weekday == "dienstag":
        print(f"Today is vinstag (so don't foget your stamp cards) and here is today's menu:")
    elif MensaURL().weekday == "mittwoch":
        print(f"Today is mojitwoch and here is today's menu:")
    else:
        print(f"Today is {MensaURL().weekday} and here is today's menu:")

    # Get the weather at Fluntern (8044)
    hour = 12 if args.time == "mittag" else 18
    temperature, emoji = get_weather(8044, hour)
    print(f"The weather at {hour}:00 is {emoji} and {int(temperature)} °C.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--time", type=str, choices=["mittag", "abend"], default="mittag", help="Time of day"
    )
    parser.add_argument("--logging", action="store_true", help="Enable logging")
    args = parser.parse_args()

    if args.logging:
        logging.basicConfig(level=logging.INFO)

    main(args)
