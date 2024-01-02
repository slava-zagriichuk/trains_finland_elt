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
Why ELT? Because of relatively small size of a single response (20-30kB), it makes sense to extract and load the data first and to process it then. As separate processes.

In this example I will start with 45 days forward from the day of request for the most hot directions (10 directions). It implies that the speed of data producing will be 45 * 10 * [20-30] kB = 10-15 MB per 1 day (1 - 1.5 MB per 1 direction per 1 day). From this point it's possible to make evaluations of data storage and define the usage policy. Like how long to store the data, how often to backup and so on.

The amount of data stored could be significantly reduced by using some SQL-type DBS. Because the major part of every response are names of variables and signs, and data could be represented as tables naturally.

I preferred Shell-script to make Extract and Load, because it's both not so difficult to make and it's native for the most servers (easy to deploy). The file structure is: Main Folder / Direction Folder (from-to) / yyyy-mm-dd (date of request).txt files.

I preferred Python to parse the responses (Transform) because it's much easier to develop and maintain. Especially if I don't know exactly what I want to make out of the data so far (apart from parsing and turning it into tables).

### Scaling
It's very easy to scale technically, because the only thing to do is to add (modify) directions to file. However, to make all this clear - it's necessary to deal with VR about using their data. I don't really think they have that weak servers to receive a few hundreds requests from this prototype program, but it MUST BE taken into account if scaling.

### Caring for others
To avoid any server overload issues and bad user experience - I'm going to plan requests in the early morning Finnish time, for example 3 AM.

Apparently, it's possible to make a predicative model to lower the amount of requests in the future.

## FILES
1) **payload.json** - payload to the POST request. Contains 3 placeholders {{}} for departure station, arrival station and date of departure.

2) **request.sh** - script for a single request.

IN: arrival station acronym, departure station acronym and the date of departure (as the keys)

OUT: raw json as a response

3) **stations_dict.csv** - a table with all the stations inner acronyms (ex. Helsinki -> HKI). This file is not in use, just to be aware of acronyms.

4) **directions.txt** - list of directions. Format: FROM TO

5) **config.txt** - list of macro-parameters.

6) **extract_load.sh** - the main script, which load all the raw responses for each direction

7) transform.py - turning the raw files into csv format (to add them to SQL tables easily then)
