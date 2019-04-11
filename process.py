#!/usr/bin/env python3

from glob import glob
from shutil import copy
from os import path, system
from datetime import datetime


if system('docker-compose up mapper'):
    if system('docker-compose up cleaner'):
        cwd = path.dirname(path.realpath(__file__))

        src_dir = path.join(cwd, 'volumes', 'cleaner', 'output')
        src = glob(path.join(src_dir, '*_listings_unique.csv'))
        if len(src) > 0:
            src = src[0]

        dest = path.join(cwd, 'volumes', 'geolocator', 'data')

        try:
            copy(src, dest)
        except Exception as e:
            print("Could not copy cleaned listings for geolocator")
            print(e)

        system('docker-compose up geolocator')

    else:
        print('Cleaner failed')

else:
    print("Mapper failed")
