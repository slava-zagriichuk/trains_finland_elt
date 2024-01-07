# trains_finland_elt
Collecting information about the availability and prices of trains in Finland

---
**IF YOU WANT TO USE IT BROADER FOR YOUR OWN PURPOSE - ASK VR.FI FIRST! I made this project as an example of ELT pipeline, it's nothing more than a prototype. THANK YOU!**

---

## INTRO
Once, while I was trying to get a cheaper train ticket on vr.fi, the thought came to my head. The calendar-price view would be so much better instead of searching each day manually. Unfortunately, the website doesn't have this instrument, so I decide to make it for my own. I found how to get all the info through a request to the hidden API.

The first project was the useful but sketchy ETL written on Python, which gives the list of prices with a couple filtering options.

Now it's an example of ELT pipeline with all the betterments I made and how it works.

## PLANNING & DESIGN

> The whole description how the program works you'll find in the architecture.pdf

The initial idea is simple: the program collects and processes information about the cost of travel for the next 1-2 months once a day. This can then be used to display the lowest prices in a calendar view.

Why ELT? Because of relatively small size of a single response (20-30kB), it makes sense to extract and load the data first and to process it then. As separate processes.

In this example I will start with 45 days forward from the day of request for the most hot directions (10 directions). It implies that the speed of data producing will be 45 * 10 * [20-30] kB = 10-15 MB per 1 day (1 - 1.5 MB per 1 direction per 1 day). From this point it's possible to make evaluations of data storage and define the usage policy. Like how long to store the data, how often to backup and so on.

The amount of data stored could be significantly reduced by using some SQL-type DBS. Because the major part of every response are names of variables and signs, and data could be represented as tables naturally.

I preferred Bash-script to make Extract and Load, because it's both not so difficult to make and it's native for the most servers (easy to deploy). The file structure is: Main Folder / Direction Folder (from-to) / yyyy-mm-dd (date of request).txt files.

I preferred Python to parse the responses (Transform) because it's much easier to develop and maintain. Especially if I don't know exactly what I want to make out of the data so far (apart from parsing and turning it into tables).

I preferred Python to make a script to integrate data. As a DBS I preferred PostgreSQL. 

### Scaling
It's very easy to scale technically, because the only thing to do is to add (modify) directions to file. Even more, directions could be separated easyly between different servers.

However, to make all this clear - it's necessary to deal with VR about using their data. I don't really think they have that weak servers to have any problems with receiving a few hundreds requests from this prototype program, but it MUST BE taken into account if scaling.

### Caring for others
To avoid any server overload issues and bad user experience - I suppose to plan requests in the early morning Finnish time, for example 3 AM.

Apparently, it's possible to make a predicative model to lower the amount of requests in the future.

## FILES
1) **payload.json** - payload to the POST request. Contains 3 placeholders {{}} for departure station, arrival station and date of departure.

2) **stations_dict.txt** - a dictionary with all the stations inner acronyms (ex. Helsinki -> HKI). This file is not in use, just to be aware of acronyms.

3) **directions.txt** - list of directions. Format: FROM TO

4) **config.txt** - list of macro-parameters.

5) **request.sh** - script for a single request to API.

6) **extract_load.sh** - the main script, which load all the raw responses for each direction to the file structure.

7) **processing.py** - functions for turning the raw files into csv format (to add them to DBS easily then).

8) **parameters.py** - functions for obtaining all the parameters to define what/where to process.

9) **transform.py** - executive python script for files with raw data transformation.

10) **psql.py** - functions for data integration into a postgresql database.

11) **create_tables.py** - executive python script to create the infrastructure of tables, views and triggers to allow loading data there.

12) **integrate.py** - executive python script for integration of transformed data into DBS.

13) **architecture.pdf** - graphically described alghorithms.

## OBSERVATIONS

1) I was wrong about the size of 1 request, it was underestimated. Because of larger amount of trains on the hot directions, the average request is getting 60kB response. Hence, the first estimations must be doubled

2) I couldn't figure out how to avoid creating 2 variables for content and connection info for logging in request.sh script. Maybe it's not even possible using shell.

3) 450 requests took 6-7 minutes, ~ 1 request per 1 second. If scaling - it makes sense to think about parallel processing, because the time to establish the connection is 0.1 sec. And the rest 90% is just waiting.

4) After inspection number of responses, I came to decision to include to the processed table trip info, train info, regular price and seats available for econom class.

5) There were two unexpected problems I faced and solved. Commuter trains, they have no available seats option; trips with transfer(s), they don't affect result, but it's possible to add the column 'Direct'.

Actually, there is a lot of attributes for seats types and availability. It's quite possible to figure out how to deal with them (study over the train types and seats arrangement is required). This way it's possible to analyze, for example, how often people carry bikes or pets by train, how in demand the first class seats are.

6) Processing takes seconds and reduces file size by about 30 times.

7) Integration takes dozens of seconds (depending on speed of DBS)

## HOW TO USE

1) In config.txt define the destination folder _(where all the files will be kept and used)_ and how much days _(from the day of request)_ you want to know trains journeys. For example:

DESTINATION_FOLDER="/user/documemts/VR_journeys"

DAYS_FORWARD=45

2) In directions.txt write all the directions you want to follow. Use the following format: Departure station + space + Arrival station. Each direction starts on a new line. List of acronyms for stations you can find in station_dict.txt.

3) Create the file "database.ini" with connection parameters to db you will use (as an administrator). **Don't share it to anyone. Don't show it to anyone**. By default it's postgres db, the configs section must begin with [postgresql] line.

4) Execute createtables.py. Execute it each time manually after you add directions.

5) Add to planner one after another _(next one has to launch after previous being finished)_: 

extract_load.sh -> transform.py -> integrate.py

Preferrably, plan extract_load to the early morning once a day (though, it's up to you).

6) Create users: "webDeveloper" with only read only rights for only materialized views; "dataScientist" with read only rights for only tables.

_All the functions works well with default parameters, but they also have an additional functionality. You can check them out in docstrings._

## RESULTS

1) On the Extract-Load stage in the destination folder the following file system is created:

[folders] HKI TPE ; HKI TKU; TPE HKI ; TKU HKI ...

Files, following the date of request in each folder:

[files] 2024-01-01.txt ; 2024-01-02.txt ; 2024-01-03.txt ...

2) On the Transform stage these files are processed and written with the same names but .csv instead of .txt.

3) On the Integration stage files are integrated to Postgres db:

For each direction table, 2 materialized views and insert/update trigger are created. For example, for direction HKI TPE there are table hki_tpe, materialized views hki_tpe_current and hki_tpe_price_range and trigger hki_tpe_trigger. All the materialized view were refreshed by the prescribed function.

4) For each process log files have been created respectfully.
