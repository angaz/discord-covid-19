import logging

from discord_covid19 import Covid19Client


def read_token_file(filename="discord.token"):
    with open(filename) as f:
        token = f.read().strip()
    return token


def main():
    logging.basicConfig(level=logging.INFO)
    client = Covid19Client()
    client.run(read_token_file())


if __name__ == "__main__":
    main()
