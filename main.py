import argparse
import json
import logging

from src.constants import MensaNames, MensaURL
from src.scraping import get_menus
from src.utils import print_menu
from src.weather import get_weather
from src.question import get_random_question


def main(args):
    menu_df = get_menus()
    question = get_random_question(0 if args.time == "mittag" else 1)

    print_welcome_message(args)
    if question is not None:
        print("🧠 " + question[0])
    print() 

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

    if question is not None:
        print("💡 " + question[1])

def print_welcome_message(args):
    # with open("data/messages.json", "r") as f:
    #     messages = json.load(f)
    # greeting_msg = np.random.choice(messages["welcome-messages"])
    # print(f"{greeting_msg} Today is {MensaURL().weekday} and here is today's menu:\n")

    if MensaURL().weekday == "dienstag":
        day = "vinstag (so don't foget your stamp cards)"
    elif MensaURL().weekday == "mittwoch":
        day = "mojitwoch"
    else:
        day = MensaURL().weekday

    # Get the weather at Zürich (8001)
    hour = 12 if args.time == "mittag" else 18
    temperature, emoji = get_weather(8001, hour)

    print(f"Today is {day} ({emoji}, {int(temperature)} °C) and here is today's menu:")


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
