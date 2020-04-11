import shlex

import discord
from aiohttp import ClientSession

from .graph import graph

FUNCTIONS = {
    "graph": graph,
}


class Covid19Client(discord.AutoShardedClient):
    async def start(self, *args, **kwargs):
        self.api_session = ClientSession()
        await super().start(*args, **kwargs)

    async def close(self):
        await self.api_session.close()
        await super().close()

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        args = shlex.split(message.content)
        if args[0] in ("!c", "!covid"):
            cmd = FUNCTIONS.get(args[1])
            if cmd is not None:
                await cmd(self.api_session, message, args[1:])
            else:
                await message.channel.send(f"Command not found: `{args[1]}`")
