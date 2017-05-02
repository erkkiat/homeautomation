from datetime import datetime

# from babel.dates import format_date, format_datetime, format_time
from astral import Astral

import settings


class Sun:
    """Calculate when to expect daylight"""
    astral = None
    city = None

    def __init__(self):
        self.astral = Astral()
        # Set the location in settings.py
        self.city = self.astral[settings.LOCATION]

    def datetime(self, key):
        "Let's find out when to expect daylight"
        sun = self.city.sun(datetime.today(), local=True)
        return sun[key]
