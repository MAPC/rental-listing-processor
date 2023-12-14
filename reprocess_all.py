from datetime import datetime
import json
from math import ceil
from os import system


def parse_config(filename):
    config = {}
    with open(".env.mapper", "r") as config_file:
        for line in config_file.readlines():
            if len(line.strip()) > 0: # and not line.startswith("#"):
                key,val = line.split("=")
                config[key.strip()] = val.strip()
    return config


def run_processor():
    config = parse_config(".env.mapper")
    print("[--] Running process.py using this config:")
    print(json.dumps(config, indent=2, default=str))
    print("")

    if system('./process.py') != 0:
        print('[!!] Processing failed, exiting')
        exit(1)


MIN_YEAR = 2020
CURRENT_YEAR = datetime.now().year
CURRENT_MONTH = datetime.now().month
CURRENT_QUARTER = ceil(CURRENT_MONTH/3)

# Loop through all months/years from 2020 until now
for year in range(MIN_YEAR, CURRENT_YEAR+1):
    for month in range(1, 12 + 1):
        if year >= CURRENT_YEAR and month >= CURRENT_MONTH:
            break
        config = parse_config(".env.mapper")
        if config.get("MAPPER_QUARTER") is not None:
            config["#MAPPER_QUARTER"] = config["MAPPER_QUARTER"]
            del config["MAPPER_QUARTER"]
        config["MAPPER_YEAR"] = year
        config["MAPPER_MONTH"] = month

        # overwrite config
        with open(".env.mapper", "w") as config_file:
            config_file.write("\n".join([f"{k}={v}" for k, v in config.items()]))

        run_processor()

# Loop through all quarters from 2020 until now
for year in range(MIN_YEAR, CURRENT_YEAR+1):
    for quarter in range(1, 4 + 1):
        if year >= CURRENT_YEAR and quarter >= CURRENT_QUARTER:
            break
        config = parse_config(".env.mapper")
        if config.get("MAPPER_MONTH") is not None:
            config["#MAPPER_MONTH"] = config["MAPPER_MONTH"]
            del config["MAPPER_MONTH"]
        config["MAPPER_YEAR"] = year
        config["MAPPER_QUARTER"] = quarter

        # overwrite config
        with open(".env.mapper", "w") as config_file:
            config_file.write("\n".join([f"{k}={v}" for k, v in config.items()]))

        run_processor()

# Loop through all years from 2020 until now
for year in range(MIN_YEAR, CURRENT_YEAR+1):
    if year >= CURRENT_YEAR:
        break
    config = parse_config(".env.mapper")
    if config.get("MAPPER_MONTH") is not None:
        config["#MAPPER_MONTH"] = config["MAPPER_MONTH"]
        del config["MAPPER_MONTH"]
    if config.get("MAPPER_QUARTER") is not None:
        config["#MAPPER_QUARTER"] = config["MAPPER_QUARTER"]
        del config["MAPPER_QUARTER"]
    config["MAPPER_YEAR"] = year

    # overwrite config
    with open(".env.mapper", "w") as config_file:
        config_file.write("\n".join([f"{k}={v}" for k, v in config.items()]))

    run_processor()
