# Current Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
# Historical Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv

import asyncio
import typing
from datetime import datetime, date, timezone
from dataclasses import dataclass
from csv import DictReader
from matplotlib import pyplot as plt
import pycountry
import matplotlib.dates as mdates
from aiohttp import ClientSession


def parse_last_update(last_update: str) -> datetime:
    try:
        out = datetime.fromisoformat(last_update)
    except ValueError:
        out = datetime.strptime(last_update, "%m/%d/%y")

    return out.replace(tzinfo=timezone.utc)


def find_country(country_region: str) -> pycountry.ExistingCountries:
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

    if country_region in known:
        return known[country_region]
    else:
        return pycountry.countries.search_fuzzy(country_region)[0]


@dataclass(frozen=True)
class CountryDayData:
    day: date
    country_region: str
    last_update: datetime
    confirmed: int
    deaths: int
    recovered: int

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
    last_update: datetime
    days: typing.List[DayData]

    def __init__(
        self, country_region: str, last_update: datetime, days: typing.List[DayData]
    ):
        self.country_region = country_region
        self.country = find_country(country_region)
        self.last_update = last_update
        self.days = days

    def to_dict(self) -> dict:
        return {
            "country_region": self.country_region,
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


async def download_csv_file(
    session: ClientSession, url: str, day: typing.Optional[date] = None
) -> CountryDayDataList:
    async with session.get(url) as resp:
        rows = DictReader((await resp.text()).splitlines())
        return [CountryDayData.init_csv_row(row, day) for row in rows]


async def download_current_data(session: ClientSession) -> CountryDayDataList:
    return await download_csv_file(
        session,
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv",
        datetime.utcnow().date(),
    )


async def download_historical_data(session: ClientSession) -> CountryDayDataList:
    return await download_csv_file(
        session,
        "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv",
    )


def group_country_region(data: CountryDayDataList) -> CountryDataList:
    data.sort(key=lambda d: d.day)
    data.sort(key=lambda d: d.country_region)

    output_list = []
    current_list = [data[0]]
    for current in data[1:]:
        if current.country_region == current_list[0].country_region:
            current_list.append(current)
        else:
            output_list.append(
                CountryData(
                    current_list[0].country_region,
                    max(current_list, key=lambda a: a.last_update).last_update,
                    [
                        DayData(day.day, day.confirmed, day.deaths, day.recovered)
                        for day in current_list
                    ],
                )
            )
            current_list = [current]

    return output_list


async def initialize_data(session: ClientSession) -> CountryDataList:
    data = [
        row
        for day in [
            await download_historical_data(session),
            await download_current_data(session),
        ]
        for row in day
    ]

    return group_country_region(data)


def axes_confirmed_since_nth_case(country: CountryData, since_nth_case: int):
    x, y = country.axes_confirmed()
    offset = [i >= since_nth_case for i in y].index(True)
    return offset, x, y


def graph_since_nth_case(
    data: CountryDataList, country_names: typing.Sequence[str], since_nth_case: int,
):
    country_codes = [
        pycountry.countries.search_fuzzy(cn)[0].alpha_2 for cn in country_names
    ]
    countries = [
        (c, *axes_confirmed_since_nth_case(c, since_nth_case))
        for c in data
        if (c.country and c.country.alpha_2 in country_codes)
        or c.country_region in country_names
    ]
    first_country = [
        c
        for c in countries
        if (c[0].country and c[0].country.alpha_2 == country_codes[0])
        or c[0].country_region == country_codes[0]
    ][0]
    length = len(first_country[3]) - first_country[1]

    plt.figure()
    plt.style.use("discord.mplstyle")

    for country, offset, x, y in countries:
        if offset == -1:
            continue

        off_len = offset + length
        y_plot = y[offset:off_len]
        plt.plot(
            range(len(y_plot)),
            y_plot,
            marker="o",
            label=(
                f"{country.country.name} ({offset} days offset)"
                if since_nth_case
                else country.country.name
            ),
        )

    plt.xlabel(
        f"Days since {since_nth_case}th case ({length} days for {first_country[0].country.name})"
    )
    plt.ylabel("Number of cases")
    plt.tight_layout()
    plt.legend()
    plt.savefig("fig_since_nth.png")


def graph(
    data: CountryDataList, country_names: typing.Sequence[str],
):
    country_codes = [
        pycountry.countries.search_fuzzy(cn)[0].alpha_2 for cn in country_names
    ]
    countries = [
        (c, *c.axes_confirmed())
        for c in data
        if (c.country and c.country.alpha_2 in country_codes)
        or c.country_region in country_names
    ]

    plt.figure()
    plt.style.use("discord.mplstyle")

    for country, x, y in countries:
        plt.plot(x, y, marker="o", label=country.country.name)

    plt.xlabel("Date")
    plt.ylabel("Number of cases")
    plt.tight_layout()
    plt.legend()
    plt.savefig("fig.png")


async def _main():
    async with ClientSession() as session:
        data = await initialize_data(session)

    graph(data, ["South Africa"])
    graph_since_nth_case(data, ["South Africa", "Italy", "KR", "Czech Republic"], 0)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
