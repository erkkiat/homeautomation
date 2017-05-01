from datetime import datetime

# from babel.dates import format_date, format_datetime, format_time
from astral import Astral

import settings


class Sun:
    astral = None
    city = None

    def __init__(self):
        self.astral = Astral()
        self.city = self.astral[settings.LOCATION]

    def datetime(self, key):
        sun = self.city.sun(datetime.today(), local=True)
        return sun[key]
