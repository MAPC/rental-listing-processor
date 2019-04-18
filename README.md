# Rental Listing Processor

This program orchestrates Docker containers together to run the steps to 
process the rental listings data. 

### Containers

- [Mapper](https://github.com/mapc/rental-listing-mapper)
- [Cleaner](https://github.com/mapc/rental-listing-cleaner)
- [Geolocator](https://github.com/mapc/rental-listing-geolocator)


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

There is one environment file that is loaded into the Mapper container which you must 
specify the year and quarter which are pulling listings data for and add database information to. 
The only container that does any communication with the database is the Mapper (I will get to what 
this container does below).

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


### Running

```sh
./process.py
```

### Container Descriptions
#### Mapper: Retrieve and transform the data

The Mapper container pulls the data from the database according to the months specified in 
the `map` program. We need the Mapper because the Cleaner container wants the input data in a
specific format/structure. The Mapper is responsible for shaping the timely data into a consumable
CSV file.

#### Cleaner: Categorize and standardize the data

The Cleaner generates a few of the deliverables while also organizing input datasets for the
Geolocator to process. After the cleaner runs, we have to manually move one of the files it
creates so the Geolocator has access to it. 

#### Geolocator: Geolocate datapoints and create some charts

The final step is running the Geolocator. This takes the longest of all processing steps, usually 
5-8 hours.


### Harvesting Deliverables

You should now see a _.zip_ archive in the project root which contains the output of the process.
