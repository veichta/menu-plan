import datetime
from enum import Enum


class MensaNames(Enum):
    uzh_oben = "uzh_oben"
    uzh_unten = "uzh_unten"
    uzh_abend = "uzh_abend"
    platte = "platte"
    poly = "poly"
    poly_abend = "poly_abend"
    wok = "wok"


class MensaURL:
    def __init__(self):
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        weekdays = ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"]
        self.weekday = weekdays[datetime.datetime.now().weekday()]

        if self.weekday in ["samstag", "sonntag"]:
            raise ValueError("No Mensa on weekends")

    def uzh_oben(self):
        """Get URL for UZH Mensa Oben

        Returns:
            str: URL
        """
        return f"https://www.mensa.uzh.ch/de/menueplaene/zentrum-mensa/{self.weekday}.html"

    def uzh_unten(self):
        """Get URL for UZH Mensa Unten

        Returns:
            str: URL
        """
        return f"https://www.mensa.uzh.ch/de/menueplaene/zentrum-mercato/{self.weekday}.html"

    def uzh_abend(self):
        """Get URL for UZH Mensa Abend

        Returns:
            str: URL
        """
        return f"https://www.mensa.uzh.ch/de/menueplaene/zentrum-mercato-abend/{self.weekday}.html"

    def platte(self):
        return f"https://www.mensa.uzh.ch/de/menueplaene/platte-14/{self.weekday}.html"

    def poly(self):
        """Get URL for Poly Mensa

        Returns:
            str: URL
        """
        return (
            "https://idapps.ethz.ch/cookpit-pub-services/v1/weeklyrotas/?client-id=ethz-wcms"
            + "&lang=de&rs-first=0"
            + "&rs-size=50"
            + "&valid-after={valif_after}"
            + "&valid-before={valid_before}"
            + "&facility=9"
        )
        # return (
        #     "https://ethz.ch/de/campus/erleben/gastronomie-und-einkaufen/gastronomie/menueplaene"
        #     + f"/offerDay.html?language=de&id=9&date={self.date}"
        # )

    def poly_abend(self):
        """Get URL for Poly Mensa Abend

        Returns:
            str: URL
        """
        return (
            "https://idapps.ethz.ch/cookpit-pub-services/v1/weeklyrotas/?client-id=ethz-wcms"
            + "&lang=de&rs-first=0"
            + "&rs-size=50"
            + "&valid-after={valif_after}"
            + "&valid-before={valid_before}"
            + "&facility=9"
        )

    def wok(self):
        """Get URL for Clausiusbar

        Returns:
            str: URL
        """
        return (
            "https://idapps.ethz.ch/cookpit-pub-services/v1/weeklyrotas/?client-id=ethz-wcms"
            + "&lang=de&rs-first=0"
            + "&rs-size=50"
            + "&valid-after={valif_after}"
            + "&valid-before={valid_before}"
            + "&facility=3"
        )

    def get_url(self, mensa: MensaNames):
        """Get URL for Mensa

        Args:
            mensa (MensaNames): Mensa

        Returns:
            str: URL
        """
        if not hasattr(self, mensa.value):
            raise ValueError(f"There is no ULR for {mensa.value}.")
        return getattr(self, mensa.value)()
