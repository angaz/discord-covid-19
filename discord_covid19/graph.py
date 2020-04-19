import typing
import urllib
from time import time_ns

import discord
from aiohttp import ClientSession

from country_day_data import country_to_identifier


def group_args(args: typing.Sequence[str]) -> typing.Dict[str, typing.List[str]]:
    out = {"nonce": time_ns()}
    key = None
    current_array = []

    for arg in args:
        if arg in ("countries", "scale", "series", "since"):
            if key is not None and current_array:
                out[key] = current_array
            key = arg
            current_array = []
        else:
            current_array.append(arg)

    if key is not None and current_array:
        out[key] = current_array

    return out


def parse_args(args: typing.Sequence[str]) -> typing.Dict[str, str]:
    grouped_args = group_args(args)
    if "countries" in grouped_args:
        grouped_args["countries"] = ",".join(
            [country_to_identifier(country) for country in grouped_args["countries"]]
        )

    if "scale" in grouped_args:
        if len(grouped_args["scale"]) != 1:
            raise ValueError("Scale should have exactly 1 value.")
        grouped_args["scale"] = grouped_args["scale"][0]

    if "series" in grouped_args:
        grouped_args["series"] = ",".join(grouped_args["series"])

    if "since" in grouped_args:
        if len(grouped_args["since"]) != 1:
            raise ValueError("Since should have exactly 1 value.")
        grouped_args["since"] = grouped_args["since"][0]

    return grouped_args


async def graph(
    session: ClientSession, message: discord.Message, args: typing.Sequence[str]
):
    parsed_args = parse_args(args)
    print(parsed_args)

    qs = urllib.parse.urlencode(parsed_args)
    url = f"https://covid19.angusd.com/graph?{qs}"
    print(url)

    embed = discord.Embed()
    embed.set_image(url=url)
    await message.channel.send(embed=embed)
