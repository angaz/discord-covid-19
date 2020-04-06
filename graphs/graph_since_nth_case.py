import asyncio
from io import BytesIO

from matplotlib import pyplot as plt

from country_day_data import CountryData, CountryDataList


def offset_since_confirmed(country: CountryData, since_nth_case: int) -> int:
    x, y = country.confirmed_axes()
    return [i >= since_nth_case for i in y].index(True)


def st_nd_th(since_nth_case: int) -> str:
    rem = since_nth_case % 10
    if since_nth_case != 11 and rem == 1:
        return f"{since_nth_case}st"
    if since_nth_case != 12 and rem == 2:
        return f"{since_nth_case}nd"
    return f"{since_nth_case}th"


def _graph_since_nth_case(
    countries: CountryDataList, title: str, since_nth_case: int,
) -> BytesIO:
    countries = [
        (c, l, offset_since_confirmed(c, since_nth_case), (x, y))
        for c, l, (x, y) in countries
    ]
    first_country = countries[0]
    length = len(first_country[3][1]) - first_country[2]

    fig, ax = plt.subplots()

    for country, label, offset, (x, y) in countries:
        if offset == -1:
            continue

        off_len = offset + length
        y_plot = y[offset:off_len]
        ax.plot(
            range(len(y_plot)),
            y_plot,
            marker="o",
            label=(
                f"{label} ({offset:+} Day{'s' if offset != 1 else ''})"
                if since_nth_case
                else label
            ),
        )
        ax.annotate(
            y_plot[-1],
            xy=(1, y_plot[-1]),
            xytext=(5, -5),
            xycoords=("axes fraction", "data"),
            textcoords="offset pixels",
        )

    ax.set_title(f"{title} vs Days Since {st_nd_th(since_nth_case)} Confirmed Case")
    ax.set_xlabel(
        f"Days Since {st_nd_th(since_nth_case)} Confirmed Case "
        f"({length} Day{'s' if length != 1 else ''} for {first_country[0].country.name})"
    )
    ax.set_ylabel(f"Number of {title}")
    ax.legend()
    fig.tight_layout()

    buf = BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    return buf


async def graph_since_nth_case(
    countries: CountryDataList, title: str, since_nth_case: int
) -> BytesIO:
    return await asyncio.get_event_loop().run_in_executor(
        None, _graph_since_nth_case, countries, title, since_nth_case
    )
