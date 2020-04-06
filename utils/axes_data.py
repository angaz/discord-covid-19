import typing
from datetime import date

from country_day_data import CountryData, CountryDataList

from .series_label import series_label


def axes_data(
    countries: CountryDataList, series: typing.Sequence[str]
) -> typing.List[
    typing.Tuple[CountryData, str, typing.Tuple[typing.List[date], typing.List[int]]]
]:
    multi_series = len(series) > 1

    def get_one(c: CountryData, s: str):
        if s == "confirmed":
            return (
                c,
                series_label(c.country.name, s, multi_series),
                c.confirmed_axes(),
            )
        if s == "deaths":
            return (c, series_label(c.country.name, s, multi_series), c.deaths_axes())

    return [get_one(c, s) for c in countries for s in series]
