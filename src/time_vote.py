import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--time",
        type=str,
        choices=["mittag", "abend"],
        default="mittag",
        help="Time to vote for. Format: HH:MM",
    )
    args = parser.parse_args()

    mittag_message = (
        "Let's settle this once and for all! It's time for the lunchtime vote!\n\n"
        + "🥐11:00 Let's lunch like we're having brunch!\n"
        + "🤝11:30: Late enough to be fashionable, early enough to beat the crowd!\n"
        + "🐍12:00 It's the traditional lunch hour, let's stick to the classics!\n"
        + "💀12:30: Who needs lunch when you can just snack all day?\n"
    )

    abend_message = (
        "Let's settle this once and for all! It's time for the dinnertime vote!\n\n"
        + "🤡17:00 Let's have an early bird dinner and catch the sunset!\n"
        + "👌17:30: Perfect timing for those who can't wait to eat but don't want to be too early!\n"
        + "🚎18:00: The classic dinner time! Let's stick to tradition!\n"
        + "🍻18:30: For those who like to take their time and enjoy a drink before dinner!\n"
        + "🌚19:00 Let's have a late dinner and make it a night to remember!\n\n"
    )

    if args.time == "mittag":
        print(mittag_message)
    elif args.time == "abend":
        print(abend_message)


if __name__ == "__main__":
    main()
