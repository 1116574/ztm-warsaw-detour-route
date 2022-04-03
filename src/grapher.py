import json
from collections import defaultdict
from rich import print

# TODO: Somehow parse *WK from ztm to get more connections
# TODO: Parse "location" field as an alternative road name

# : P+R Al. Krakowska – … – Chałubińskiego – al. Jana Pawła II – Stawki – … – MARYMONT-POTOK

# SIGMA.JS FORMAT
node = {
    "key": "2.0",
    "attributes": {
        "x": 248.45229,
        "y": 52.22656,
        "size": 16.714285,
        "label": "MlleBaptistine",
        "color": "#BB100A"
      }
}

edge = {
    "key": "0",
    "source": "1.0",
    "target": "0.0",
    "attributes": {
        "size": 1
    }
}
#/ SIGMA.JS FORMAT

nodes = []
edges = []

already_added_nodes = []
already_added_edges = []

class StopPart:
    """ Object that holds refences to previous object like a list, but this can store multible references allowing for branching """
    def __init__(self, my_id, road, *args):
        self.my_id = my_id
        self.road = road
        self.parents = args
        print(self.parents)
    
    def __repr__(self) -> str:
        if type(self.parents[0]) is str:
            return '<' + ', '.join(self.parents) + '→' + self.my_id + ' | ' + self.road + '>'
        else:
            return '<START' + '→' + self.my_id + ' | ' + self.road + '>'


FILE = False

with open('routes.json', 'r') as f:
    routes = json.load(f)

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)


_i = 0

road_matrix = {'stop': 'roadname'}

for line in routes:
    # Save only trams
    if not routes[line]["type"] in ["LINIA TRAMWAJOWA", "LINIA TRAMWAJOWA OKRESOWA"]:
        continue

    for r in routes[line]["routes"]:
        
        roads = {"roadname": ["stop1", "stop2", "stop3"]}
        roads = defaultdict(list)
        current_road = ""
        route = routes[line]["routes"][r]["route_details"]
        previous_stop = None

        for event in route:
            if event["type"] == "road_change":
                current_road = event["road"]
            elif event["type"] == "stop":
                # assuming for now that every route starts with a road_change
                # roads[current_road].append(stops[event["id"][:4]][event["id"][4:]])
                if event["id"][4:5] == '7':
                    continue
                
                if FILE:
                    if event["id"] not in already_added_nodes:
                        already_added_nodes.append(event["id"])
                        try:
                            x = float(stops[event["id"][:4]][event["id"][4:]]["X"])
                            y = float(stops[event["id"][:4]][event["id"][4:]]["Y"])
                            num = event["id"][4:]
                        except (ValueError, KeyError):
                            x = 21.05
                            y = 52.20
                            num = "XX"

                        try:
                            # Chopin airport be like:
                            # print(stops[event["id"][:4]])
                            name = stops[event["id"][:4]]["name"].strip().strip(',')
                        except KeyError:
                            name = "no name provided"
                            x = 21.05
                            y = 52.20
                            print('!?', event["id"])

                        nodes.append({
                            "key": event["id"],
                            "attributes": {
                                "x": x,
                                "y": y,
                                "label": name + " " + num,
                                "size": 4.0,
                                # "color": MODE_COLOR,
                                "road_name": current_road
                            }
                        })


                if previous_stop and (event["id"], previous_stop) not in already_added_edges:
                    road_matrix[event["id"]] = current_road  # Not needed for core
                    already_added_edges.append((event["id"], previous_stop))
                    edges.append({
                        "key": _i,
                        "source": previous_stop,
                        "target": event["id"],
                        "attributes": {
                            "size": 2.0,
                            "type": "arrow",
                            # "colors": MODE_COLOR
                        }
                    })
                _i += 1

                previous_stop = event["id"]


# Now instead of having (*parents) -> stop convert to stop -> (*children)
new_form = {'stop': ['child1', 'child2']}
new_form = defaultdict(list)
for edg in edges:
    # No duplicate is ensured by edges generation
    new_form[edg['source']].append(edg['target'])


with open('trams.json', 'w') as f:
    json.dump(new_form, f, indent=4)

with open('road_matrix.json', 'w') as f:
    json.dump(road_matrix, f, indent=4)

if FILE:
    with open('data.json', 'w') as f:
        json.dump({
            "nodes": nodes,
            "edges": edges
        }, f, indent=4)
