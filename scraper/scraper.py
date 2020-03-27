# Current Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
# Historical Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv

import asyncio
import typing
from datetime import datetime, date, timezone
from dataclasses import dataclass
from csv import DictReader
from pathlib import Path
from matplotlib import pyplot as plt

import json

from aiohttp import ClientSession

DATABASE_FILE = Path("database.json").resolve()


def parse_last_update(last_update: str) -> datetime:
    try:
        out = datetime.fromisoformat(last_update)
    except ValueError:
        out = datetime.strptime(last_update, "%m/%d/%y")

    return out.replace(tzinfo=timezone.utc)


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
    last_update: datetime
    days: typing.List[DayData]

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

    out = group_country_region(data)
    with DATABASE_FILE.open("w") as f:
        json.dump([o.to_dict() for o in out], f)

    return out


def get_axes_confirmed(
    country: CountryData, since_nth_case: typing.Optional[int] = None
) -> typing.Tuple[CountryData, int, typing.List[int], typing.List[date]]:
    x = [d.day for d in country.days if d.confirmed > 0]
    y = [d.confirmed for d in country.days if d.confirmed > 0]

    if since_nth_case:
        offset = [i >= since_nth_case for i in y].index(True)
        return country, offset, x, y
    else:
        return country, 0, x, y


def plot_sa(
    data: CountryDataList,
    country_names: typing.Sequence[str],
    since_nth_case: typing.Optional[int] = None,
):
    countries = [
        get_axes_confirmed(c, since_nth_case)
        for c in data
        if c.country_region in country_names
    ]
    shortest_country = min(*[c for c in countries], key=lambda c: len(c[3]) - c[1])
    length = len(shortest_country[3]) - shortest_country[1]

    plt.style.use("discord.mplstyle")

    for country, offset, x, y in countries:
        if since_nth_case is not None:
            if offset == -1:
                continue

            off_len = offset + length
            y_plot = y[offset:off_len]
            plt.plot(
                range(length), y_plot, marker="o", label=country.country_region,
            )

        else:
            plt.plot(x, y, marker="o", label=country.country_region)

    if since_nth_case is not None:
        plt.xlabel(
            f"Days since {since_nth_case}th case ({length} days for {shortest_country[0].country_region})"
        )
    else:
        plt.xlabel("Date")

    plt.ylabel("Number of cases")
    plt.tight_layout()
    plt.legend()
    plt.savefig("fig.png")


async def _main():
    async with ClientSession() as session:
        data = await initialize_data(session)

    plot_sa(data, ["South Africa", "Italy", "Korea, South"], 5)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
