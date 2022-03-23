# detour-route-maker
Create gtfs-like shapes for detoured Warsaw trams only using road names

Eg. with just `'ŻERAŃ FSO - … - most Gdański - Słomińskiego - Okopowa - … - BOERNEROWO'` (along with original stops) you can get list of waypoints and stops in this altered route

## Usage/how it works
First, we need to get data from ZTM, specifically `routes.json` and `stop_groups.json` genereted by [my other project](https://github.com/1116574/ztm-warsaw-timetable-parser)

This gets proccessed further by `grapher.py` which generates `trams.json` - a node/edge graph, and `road_matrix.json` - a list of all stops and what street they are on.

Now you can run `route_finder.py` and hope for the best lol

## Messy code ahead
This was created in spare time, as an experiment. Code quality wasnt the biggest concern as much as getting it to work lol

This has gone thruogh many iterations, and rewrite would seem as best option but i am too lazy for that and opted to black box it

## Why only trams?
In *theory* this approach can work for busses, but since their detours are on streets that cant be graphed automatically (trams can only run on rails), and the sheer amount of routes, roads, and stops makes debugging a nightmare, I decided against it.