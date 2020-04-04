import typing
import pycountry
from matplotlib import pyplot as plt
from pathlib import Path


from country_day_data import CountryDataList, CountryData


def axes_confirmed_since_nth_case(country: CountryData, since_nth_case: int):
    x, y = country.axes_confirmed()
    offset = [i >= since_nth_case for i in y].index(True)
    return offset, x, y


def graph_since_nth_case(
    data: CountryDataList,
    outdir: Path,
    country_names: typing.Sequence[str],
    since_nth_case: int,
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

    fig, ax = plt.subplots()

    for country, offset, x, y in countries:
        if offset == -1:
            continue

        off_len = offset + length
        y_plot = y[offset:off_len]
        ax.plot(
            range(len(y_plot)),
            y_plot,
            marker="o",
            label=(
                f"{country.country.name} ({offset} days offset)"
                if since_nth_case
                else country.country.name
            ),
        )

    ax.set_xlabel(
        f"Days since {since_nth_case}th case ({length} days for {first_country[0].country.name})"
    )
    ax.set_ylabel("Number of cases")
    ax.legend()
    fig.tight_layout()
    fig.savefig(outdir / "graph_since_nth.png")
