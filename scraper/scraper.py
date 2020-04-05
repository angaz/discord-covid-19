import typing
from csv import DictReader
from datetime import date, datetime
from itertools import groupby

from aiohttp import ClientSession

from country_day_data import (
    CountryData,
    CountryDataList,
    CountryDayData,
    CountryDayDataList,
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

    out_data = {
        c[0].identifier: CountryData(
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
    }

    data.sort(key=lambda d: d.day)
    out_data["GLOBAL"] = CountryData(
        "Global",
        max(data, key=lambda d: d.last_update).last_update,
        [
            DayData(
                days[0].day,
                sum(d.confirmed for d in days),
                sum(d.deaths for d in days),
                sum(d.recovered for d in days),
            )
            for days in (list(d) for _, d in groupby(data, key=lambda d: d.day))
        ],
    )

    return out_data


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
