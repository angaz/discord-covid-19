from dataclasses import dataclass
import typing
from datetime import datetime, date, timezone
import pycountry

FOUND_COUNTRIES = {}


def parse_last_update(last_update: str) -> datetime:
    try:
        out = datetime.fromisoformat(last_update)
    except ValueError:
        out = datetime.strptime(last_update, "%m/%d/%y")

    return out.replace(tzinfo=timezone.utc)


def find_country(country_region: str) -> pycountry.ExistingCountries:
    if country_region in FOUND_COUNTRIES:
        return FOUND_COUNTRIES[country_region]

    known = {
        "Burma": pycountry.countries.get(alpha_2="MM"),
        "Congo (Brazzaville)": pycountry.countries.get(alpha_2="CG"),
        "Congo (Kinshasa)": pycountry.countries.get(alpha_2="CG"),
        "Diamond Princess": None,
        "Korea, South": pycountry.countries.get(alpha_2="KR"),
        "Laos": pycountry.countries.get(alpha_2="LA"),
        "MS Zaandam": None,
        "Taiwan*": pycountry.countries.get(alpha_2="TW"),
        "West Bank and Gaza": pycountry.countries.get(alpha_2="PL"),
    }

    out = (
        known[country_region]
        if country_region in known
        else pycountry.countries.search_fuzzy(country_region)[0]
    )

    FOUND_COUNTRIES[country_region] = out
    return out


@dataclass(frozen=True)
class CountryDayData:
    day: date
    country_region: str
    last_update: datetime
    confirmed: int
    deaths: int
    recovered: int

    @property
    def identifier(self):
        country = find_country(self.country_region)
        return country.alpha_2.upper() if country else self.country_region.upper()

    @classmethod
    def init_csv_row(cls, data: dict, day: typing.Optional[date] = None):
        last_update = parse_last_update(data["Last_Update"])

        return cls(
            day or last_update.date(),
            data["Country_Region"],
            last_update,
            int(data["Confirmed"] or 0),
            int(data["Deaths"] or 0),
            int(data["Recovered"] or 0),
        )


@dataclass
class DayData:
    day: date
    confirmed: int
    deaths: int
    recovered: int

    def to_dict(self) -> dict:
        return {
            "day": self.day.isoformat(),
            "confirmed": self.confirmed,
            "deaths": self.deaths,
            "recovered": self.recovered,
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            date.fromisoformat(data["day"]),
            data["confirmed"],
            data["deaths"],
            data["recovered"],
        )


@dataclass
class CountryData:
    country_region: str
    country: pycountry.ExistingCountries
    identifier: str
    last_update: datetime
    days: typing.List[DayData]

    def __init__(
        self, country_region: str, last_update: datetime, days: typing.List[DayData]
    ):
        self.country_region = country_region
        self.country = find_country(country_region)
        self.last_update = last_update
        self.days = days
        self.identifier = (
            self.country.alpha_2.upper()
            if self.country
            else self.country_region.replace(" ", "_").upper()
        )

    def to_dict(self) -> dict:
        return {
            "country_region": self.country_region,
            "identifier": self.identifier,
            "last_update": self.last_update.isoformat(),
            "days": [day.to_dict() for day in self.days],
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["country_region"],
            data["last_update"],
            [DayData.from_dict(day) for day in data["days"]],
        )

    def x_axis(self) -> typing.List[str]:
        return [d.day for d in self.days if d.confirmed > 0]

    def y_axis(self) -> typing.List[int]:
        return [d.confirmed for d in self.days if d.confirmed > 0]

    def axes_confirmed(self) -> typing.Tuple[typing.List[str], typing.List[int]]:
        return self.x_axis(), self.y_axis()


CountryDayDataList = typing.List[CountryDayData]
CountryDataList = typing.List[CountryData]