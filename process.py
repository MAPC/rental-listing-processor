#!/usr/bin/env python3

from sys import exit
from glob import glob
from os import path, system
from datetime import datetime
from random import getrandbits
from tempfile import gettempdir
from shutil import copy, copytree, make_archive, rmtree


# Define run steps for each processing component

def run_mapper():
    print("[--] Running Mapper")

    if not system('docker-compose up mapper'):
        print('[!!] Mapper failed')
        exit(1)


def run_cleaner():
    print("[--] Running Cleaner")

    if not system('docker-compose up cleaner'):
        print('[!!] Cleaner failed')
        exit(1)

    print("[--] Preparing cleaned data for geolocation")

    cwd = path.dirname(path.realpath(__file__))

    src_dir = path.join(cwd, 'volumes', 'cleaner', 'output')
    src = glob(path.join(src_dir, '*_listings_unique.csv'))
    if len(src) > 0:
        src = src[0]

    dest = path.join(cwd, 'volumes', 'geolocator', 'data')

    try:
        copy(src, dest)
    except Exception as e:
        print("[!!] Could not copy cleaned listings for geolocator")
        print(e)
        exit(1)


def run_geolocator():
    print("[--] Running Geolocator")

    if not system('docker-compose up geolocator'):
        print('[!!] Geolocator failed')
        exit(1)

    print("[--] Bundling output")

    workdir = path.join(gettempdir(), '%0x-rla-out' % getrandbits(40))
    workdir_cleaner = path.join(workdir, 'cleaner')
    workdir_geolocator = path.join(workdir, 'geolocator')

    try:
        dir_perms = 0o700
        mkdir(workdir, dir_perms)
        mkdir(workdir_cleaner, dir_perms)
        mkdir(workdir_geolocator, dir_perms)
    except OSError:
        print("[!!] Could not create %s. You will have to bundle your own output." % workdir)
        exit(1)

    cwd = path.dirname(path.realpath(__file__))
    copytree(path.join(cwd, 'volumes', 'cleaner', 'output'), workdir_cleaner) 
    copytree(path.join(cwd, 'volumes', 'geolocator', 'output'), workdir_geolocator) 

    env = {}
    with open(path.join(cwd, ".env.mapper")) as fd:
        for line in fd:
            tokens = line.split('=')
            if len(tokens) > 1:
                name, var = line.split('=')
                env[name.strip()] = str(var).strip()

    make_archive(path.join(cwd, 'rental-listings_%02d-%d' % (int(env['MAPPER_QUARTER']), int(env['MAPPER_YEAR']))), 'zip', workdir)

    try:
        rmtree(workdir)
    except OSError:
        print("[!!] Could not delete tempdir %s. Restarting machine will clear all files in temp directory." % workdir)


# Run processor

run_mapper()
run_cleaner()
run_geolocator()

print("[--] Rental Listings Processed")
