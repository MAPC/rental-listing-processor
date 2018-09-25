# Rental Listing Processor

This program orchestrates Docker containers together to run the steps to 
process the rental listings data. 

### Containers

- [Scraper](https://github.com/mapc/rental-listing-scraper)
- [Mapper](https://github.com/mapc/rental-listing-mapper)
- [Cleaner](https://github.com/mapc/rental-listing-cleaner)
- [Geolocator](https://github.com/mapc/rental-listing-geolocator)


## Processing
### Installation & Setup

#### Dependencies
- [Docker](https://www.docker.com/)
- [Docker Compose](https://https://docs.docker.com/compose/install/)
- [Git LFS](https://git-lfs.github.com/)

Docker is used to setup each environment that is specific to each piece of 
the processor. We need Docker because of how different the set of 
requirements/dependencies are for each step (Mapping, Cleaning, Geolocating).
This prevents us from going through the process of installing each individual
environment onto your host machine and relying on the host to have the correct 
packages and versions of packages to successfully run each piece of the processor.

We need Git LFS to pull down the large _volume/_ reference files required for 
processing.

#### Installation

```sh
git clone https://github.com/MAPC/rental-listing-processor
```

#### Setup

There is one environment files that is loaded into the Mapper container which you must 
add database information to. The only container that does any communication with the 
database is the Mapper (I will get to what this container does below).

The environments for the other containers are written into the _docker-compose.yml_ file.
The reason we use an environment file for the Mapper is because it requires sensitive
information that we don't want to mistakenly commit; the other containers don't require
such sensitive information and therefore can have their environments committed. 

```sh
cp .env.mapper.template .env.mapper
vim .env.mapper
```

Provide login/location information to the Mapper container by filling in the blank fields
of _.env.mapper_.

#### Additional Temporary Step

Until https://github.com/MAPC/rental-listing-mapper/issues/1  is resolved, we have to 
manually update the three months that make up the quarter which are hardcoded into the
`map` program. Once those dates have been changed, commit and push the changes to GitHub.
Our Docker container for the Mapper pulls a fresh copy from GitHub whenever it is (re)built.


### Mapper: Retrieve and transform the data

The Mapper container pulls the data from the database according to the months specified in 
the `map` program. We need the Mapper because the Cleaner container wants the input data in a
specific format/structure. The Mapper is responsible for shaping the timely data into a consumable
CSV file.

Once you have setup your _.env.mapper_ file, execute:

```sh
docker-compose up mapper
```

You will now have a CSV file in _volumes/cleaner/csv/_ named whatever `OUT_FILE_NAME` in 
_.env.mapper_ is set to.


### Cleaner: Categorize and standardize the data

The Cleaner generates a few of the deliverables while also organizing input datasets for the
Geolocator to process. After the cleaner runs, we have to manually move one of the files it
creates so the Geolocator has access to it. 

Look inside of the _docker-compose.yml_ file and ensure that the `IN_FILE_NAME` in the Cleaner's
`environment` list is set to whatever the filename is set as `OUT_FILE_NAME` from the Mapper
environment file.

```sh
docker-compose up cleaner
```

Now that the cleaner has run, we are going to copy a file of the format _${timestamp}_listings_unique.csv_
from _volumes/cleaner/output/_ and place it inside of the _volumes/geolocator/_ directory to be 
used by the Geolocator. 


### Geolocator: Geolocate datapoints and create some charts

The final step is running the Geolocator. This takes the longest of all processing steps, usually 
9-10 hours.

```sh
docker-compose up geolocator
```


### Harvesting Deliverables

You can now collect the outputs from the Cleaner and Geolocator. Collect the entirety of both
_volumes/{cleaner,geolocator}/output/_ directories. These folders should remain separate in 
final ZIP so the recipient knows which part of the process it came from. 

That's it!
