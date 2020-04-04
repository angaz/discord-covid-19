# Current Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_country.csv
# Historical Data
# https://raw.githubusercontent.com/CSSEGISandData/COVID-19/web-data/data/cases_time.csv

import typing
from datetime import datetime, date
from csv import DictReader
from aiohttp import ClientSession
from itertools import groupby

from country_day_data import (
    CountryDataList,
    CountryDayDataList,
    CountryDayData,
    CountryData,
    DayData,
)


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
    data.sort(key=lambda d: d.identifier)

    return [
        CountryData(
            c[0].country_region,
            max(c, key=lambda d: d.last_update).last_update,
            [
                DayData(
                    days[0].day,
                    sum(d.confirmed for d in days),
                    sum(d.deaths for d in days),
                    sum(d.recovered for d in days),
                )
                for days in (list(d) for _, d in groupby(c, key=lambda d: d.day))
            ],
        )
        for c in (list(c) for _, c in groupby(data, key=lambda c: c.identifier))
    ]

    # output_list = []
    # current_list = [data[0]]
    # for current in data[1:]:
    #     if current.identifier == current_list[0].identifier:
    #         current_list.append(current)
    #     else:
    #         days = [
    #             DayData(day.day, day.confirmed, day.deaths, day.recovered)
    #             for day in current_list
    #         ]

    #         output_list.append(
    #             CountryData(
    #                 current_list[0].country_region,
    #                 max(current_list, key=lambda a: a.last_update).last_update,
    #                 days,
    #             )
    #         )
    #         current_list = [current]

    # return output_list


async def initialize_data(session: ClientSession) -> CountryDataList:
    data = [
        row
        for csv_file in [
            await download_historical_data(session),
            await download_current_data(session),
        ]
        for row in csv_file
    ]

    return group_country_region(data)
