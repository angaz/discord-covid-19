# Current Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
# Historical Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv

import asyncio
import typing
from datetime import datetime, date
from csv import DictReader
from matplotlib import pyplot as plt
from aiohttp import ClientSession

from country_day_data import (
    CountryDataList,
    CountryDayDataList,
    CountryDayData,
    CountryData,
    DayData,
)
from graphs import graph, graph_since_nth_case


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


async def _main():
    async with ClientSession() as session:
        data = await initialize_data(session)

    plt.style.use("discord.mplstyle")

    graph(data, ["Czech Republic", "South Africa"])
    graph_since_nth_case(data, ["South Africa", "Italy", "KR", "Czech Republic"], 0)


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(_main())
