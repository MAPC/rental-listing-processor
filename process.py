#!/usr/bin/env python3

from sys import exit
from glob import glob
from datetime import datetime
from random import getrandbits
from tempfile import gettempdir
from os import listdir, mkdir, makedirs, path, system, unlink
from shutil import copy, copytree, make_archive, rmtree


def _clear_directory(dir):
    for fd in listdir(dir):
        if fd == '.gitkeep':
            continue

        file_path = path.join(dir, fd)

        try:
            if path.isfile(file_path):
                unlink(file_path)
            elif path.isdir(file_path):
                _clear_directory(file_path)
        except Exception as e:
            print(e)

def cwd():
    return path.dirname(path.realpath(__file__))


# Define run steps for each processing component

def clear_directories():
    _clear_directory(path.join(cwd(), 'volumes', 'cleaner', 'csv'))
    _clear_directory(path.join(cwd(), 'volumes', 'cleaner', 'output'))
    _clear_directory(path.join(cwd(), 'volumes', 'geolocator', 'data'))
    _clear_directory(path.join(cwd(), 'volumes', 'geolocator', 'output'))


def run_mapper():
    print("[--] Running Mapper")

    if system('docker-compose up mapper') != 0:
        print('[!!] Mapper failed')
        exit(1)


def run_cleaner():
    print("[--] Running Cleaner")

    if system('docker-compose up cleaner') != 0:
        print('[!!] Cleaner failed')
        exit(1)

    print("[--] Preparing cleaned data for geolocation")

    src_dir = path.join(cwd(), 'volumes', 'cleaner', 'output')
    src = glob(path.join(src_dir, '*_listings_unique.csv'))
    if len(src) > 0:
        src = src[0]

    dest = path.join(cwd(), 'volumes', 'geolocator', 'data')

    try:
        copy(src, dest)
    except Exception as e:
        print("[!!] Could not copy cleaned listings for geolocator")
        print(e)
        exit(1)


def run_geolocator():
    print("[--] Running Geolocator")

    if system('docker-compose up geolocator') != 0:
        print('[!!] Geolocator failed')
        exit(1)

    print("[--] Bundling output")

    env = {}
    with open(path.join(cwd(), ".env.mapper")) as fd:
        for line in fd:
            tokens = line.split('=')
            if len(tokens) > 1:
                name, var = line.split('=')
                env[name.strip()] = str(var).strip()

    if MAPPER_MONTH in env:
        archive_name = 'rental-listings_%s-%s' % (env['MAPPER_MONTH'], env['MAPPER_YEAR'])
    else:
        archive_name = 'rental-listings_Q%s-%s' % (env['MAPPER_QUARTER'], env['MAPPER_YEAR'])

    tempdir = path.join(gettempdir(), 'rla-out-%0x' % getrandbits(40))
    workdir = path.join(tempdir, archive_name)
    workdir_cleaner = path.join(workdir, 'cleaner')
    workdir_geolocator = path.join(workdir, 'geolocator')

    try:
        makedirs(workdir, 0o700, exist_ok=True)
    except OSError:
        print("[!!] Could not create %s. You will have to bundle your own output." % workdir)
        exit(1)

    copytree(path.join(cwd(), 'volumes', 'cleaner', 'output'), workdir_cleaner)
    copytree(path.join(cwd(), 'volumes', 'geolocator', 'output'), workdir_geolocator)

    make_archive(path.join(cwd(), archive_name), 'zip', tempdir)

    try:
        rmtree(tempdir)
    except OSError:
        print("[!!] Could not delete tempdir %s. Restarting machine will clear all files in temp directory." % workdir)


# Run processor

clear_directories()
run_mapper()
run_cleaner()
run_geolocator()

print("[--] Rental Listings Processed")
