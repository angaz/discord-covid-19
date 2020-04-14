import typing
from dataclasses import dataclass
from datetime import date, datetime, timezone

import pycountry
from aiohttp import web

FOUND_COUNTRIES = {}


def parse_last_update(last_update: str) -> datetime:
    try:
        out = datetime.fromisoformat(last_update)
    except ValueError:
        out = datetime.strptime(last_update, "%m/%d/%y")

    return out.replace(tzinfo=timezone.utc)


def find_country(iso3: str, country_region: str) -> pycountry.ExistingCountries:
    iso3_or_country = iso3 or country_region

    if iso3_or_country == "XKS":
        return pycountry.db.Data(name="Kosovo", alpha_2="XK", alpha_3="XKS")
    if iso3_or_country == "Diamond Princess":
        return pycountry.db.Data(
            name="Diamond Princess",
            alpha_2="DIAMOND_PRINCESS",
            alpha_3="DIAMOND_PRINCESS",
        )
    if iso3_or_country == "MS Zaandam":
        return pycountry.db.Data(
            name="MS Zaandam", alpha_2="MS_ZAANDAM", alpha_3="MS_ZAANDAM"
        )
    if iso3:
        country = pycountry.countries.get(alpha_3=iso3)
        if country:
            return country
    print(iso3, country_region)
    raise KeyError()


@dataclass(frozen=True)
class CountryDayData:
    day: date
    country: pycountry.ExistingCountries
    last_update: datetime
    confirmed: int
    deaths: int
    recovered: int

    @classmethod
    def init_csv_row(cls, data: dict, day: typing.Optional[date] = None):
        last_update = parse_last_update(data["Last_Update"])

        return cls(
            day or last_update.date(),
            find_country(
                data.get("iso3", data.get("ISO3")) or None, data["Country_Region"]
            ),
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
    country: pycountry.ExistingCountries
    identifier: str
    last_update: datetime
    days: typing.List[DayData]

    def __init__(
        self,
        country: pycountry.ExistingCountries,
        last_update: datetime,
        days: typing.List[DayData],
    ):
        self.country = country
        self.identifier = self.country.alpha_3
        self.last_update = last_update
        self.days = days

    def to_dict_without_days(self) -> dict:
        return {
            "country_region": self.country.name,
            "identifier": self.identifier,
            "last_update": self.last_update.isoformat(),
        }

    def to_dict(self) -> dict:
        return {
            "country_region": self.country.name,
            "identifier": self.identifier,
            "last_update": self.last_update.isoformat(),
            "days": [day.to_dict() for day in self.days],
        }

    def confirmed_days(self) -> typing.List[date]:
        return [d.day for d in self.days if d.confirmed > 0]

    def confirmed_cases(self) -> typing.List[int]:
        return [d.confirmed for d in self.days if d.confirmed > 0]

    def deaths_days(self) -> typing.List[date]:
        return [d.day for d in self.days if d.deaths > 0]

    def deaths_cases(self) -> typing.List[str]:
        return [d.deaths for d in self.days if d.deaths > 0]

    def confirmed_axes(self) -> typing.Tuple[str, typing.List[date], typing.List[int]]:
        return self.confirmed_days(), self.confirmed_cases()

    def deaths_axes(self) -> typing.Tuple[str, typing.List[date], typing.List[int]]:
        return self.deaths_days(), self.deaths_cases()


CountryDayDataList = typing.List[CountryDayData]
CountryDataList = typing.List[CountryData]


def country_to_identifier(search: str):
    try:
        pyc = pycountry.countries.search_fuzzy(search)
        return pyc[0].alpha_3
    except LookupError:
        return search.replace(" ", "_").upper()


def filter_countries(data: CountryDataList, country_names: typing.Sequence[str]):
    def find_one(cn: str):
        identifier = country_to_identifier(cn)
        if identifier in data:
            return data[identifier]
        raise web.HTTPBadRequest(
            text=(
                f"{cn} is not a valid country.\n\n"
                "You can use none, one or many country codes or names.\n"
                "If left empty, 'global' will be used.\n"
                "Both Alpha-2 and Alpha-3 country codes will work.\n"
                "Prefer country codes to names.\n\n"
                "Special names: 'Global', 'Diamond Princess', and 'MS Zaandam'"
            )
        )

    return [find_one(cn) for cn in country_names]
