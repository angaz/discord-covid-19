from configparser import ConfigParser
from os import environ

config = ConfigParser()
config.read("config.ini")

if "database" in config:
    database = config["database"]

    for key in database.keys():
        env_key = f"PG{key.upper()}"
        if env_key in environ:
            print(f"Overriding config from env: {key} = {environ[env_key]}")
            database[key] = environ[env_key]


if __name__ == "__main__":
    print(dict(config["database"]))
