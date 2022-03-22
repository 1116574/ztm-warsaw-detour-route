import json
import time

# Go over the OG stops, and when we find first occasion to detour onto 'altered' road, we take it.
# When on last of 'altered' roads, we constantly try searching for OG stops to continue on our route.
# note that this approach might not be feasible for detours that change where line ends, for this, in the future
#  we will take the last of altered route (eg. ŻĘRAŃ FSO) and try fuzzy searching in our stops so we can have a table of all possible end stops


# 20
original_stops = ["101305","101308","101203","101103","101003","100901","100803","100701","100605","100503","100401","146801","100303","116301","704702","709910","708506","500204","500304","500406","502504","506602","506704","506804","506904","507002","507102","507202","507302","507402","507602","507706","507802","505204","516306","505304","505404","505504","505601"]
original_roads = 'ŻERAŃ FSO - Jagiello\u0144ska - Targowa - al.\"Solidarno\u015bci\" - M\u0142ynarska - Obozowa - Dywizjonu 303 - Gen.Kaliskiego - BOERNEROWO'.split(' - ')[1:-1]
altered_roads = 'ŻERAŃ FSO - … - most Gdański - Słomińskiego - Okopowa - … - BOERNEROWO'.split(' - ')[2:-2]

# 4
# original_stops = ["109101","109001","108903","108803","108603","108503","108401","108303","108201","108003","107903","107803","107703","107101","106603","100303","116301","704702","709910","701607","701505","701405","701307","701203","701105","701003","708001","300105","300205","300305","300403","300505","300605","300703","300803","300905","301003","301107","301206"]
# original_roads = 'ŻERAŃ WSCH. - Annopol - Rembieli\u0144ska - Matki Teresy z Kalkuty - Odrow\u0105\u017ca - 11 Listopada - al.\"Solidarno\u015bci\" - pl.Bankowy - Marsza\u0142kowska - Pu\u0142awska - WYŚCIGI'.split(' - ')[1:-1]
# altered_roads = 'ŻERAŃ WSCH. - … - Jagiellońska - most Gdański - Słomińskiego - al. Jana Pawła II - Chałubińskiego - Nowowiejska - … - WYŚCIGI'.split(' - ')[2:-2]

# 26
# original_stops = ["200813","200805","200701","200603","200503","200403","200303","200203","200105","100104","100204","100303","116301","704702","709910","708506","500204","500304","500404","500504","500604","500704","500804","502202","500906","501002","502104","500104","501208","505704","505806","505904","506006","503408","506104","507704","506306","506406","516103","506205","506505","604706","604608","602404","602504","602604","602704","605802","605905"]
# original_roads = ["rondo Wiatraczna","Grochowska","Targowa","al.\"Solidarno\u015bci\"","Wolska","Po\u0142czy\u0144ska","Powsta\u0144c\u00f3w \u015al\u0105skich","al.Reymonta","Broniewskiego","W\u00f3lczy\u0144ska","Nocznickiego"][1:-1]
# altered_roads = 'WIATRACZNA - … - Jagiellońska - most Gdański - Słomińskiego - al. Jana Pawła II - … - METRO MŁOCINY'.split(' - ')[2:-2]

# 15
original_stops = ["401502","401504","401403","401301","401203","401103","401003","400803","400703","400603","413701","400503","400403","412103","400309","402803","415301","709005","700501","700603","701106","701204","701308","701406","701506","701608","709904","701706","701808","701906","600104","600204","600310","600314","607604","607704"]
original_roads = ["al.Krakowska","Gr\u00f3jecka","pl.Narutowicza","Filtrowa","Nowowiejska","pl.Konstytucji","Marsza\u0142kowska","pl.Bankowy","Andersa","Mickiewicza"]
altered_roads = 'P+R Al. Krakowska - … - Chałubińskiego - al. Jana Pawła II - Stawki - … - MARYMONT-POTOK'.split(' - ')[2:-2]


RECURSION_STEPS = [6, 8, 12]

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)

with open('trams.json', 'r') as f:
    connections = json.load(f)

with open('manual_connections.json', 'r', encoding='UTF-8') as f:
    m = json.load(f)
    for k in m:
        if k in connections:
            connections[k] += m[k]
        else:
            connections[k] = m[k]

with open('road_matrix.json', 'r') as f:
    road_matrix = json.load(f)

with open('manual_roads.json', 'r') as f:
    m = json.load(f)
    for k in m:
        road_matrix[k] = m[k]

recreation = []

###
def compare(road1: str, road2: str):
    road1 = road1.lower().replace(' ', '')
    road2 = road2.lower().replace(' ', '')
    return road1 == road2


### Recursive search
def searcher(current_stop, target_road=None, target_stops=[None], recursion_depth=3, max_print=8):
    # print('|'*(max_print-recursion_depth), current_stop, road_matrix[current_stop])
    if recursion_depth == 0:
        return False, []
    route = [current_stop]
    try:
        for c in connections[current_stop]:
            # print('|'*(max_print-recursion_depth), c, stops[c[:4]]["name"], road_matrix[c])
            # Check if road is good
            if road_matrix[c] == target_road:
                route.append(c)
                return True, route
            elif c in target_stops:
            # or if stop is good
                route.append(c)
                return True, route

            # Spawn new string
            suc, tmp = searcher(c, target_road=target_road, target_stops=target_stops, recursion_depth=recursion_depth-1)
            route += tmp
            if suc:
                return True, route
    except KeyError:
        pass


    return False, []

### MAIN
def main(original_stops, route_roads, altered_roads):
    og_index = 0
    alt_index = 0

    # route_roads stores currently relevant roads, depending on the context, same for index
    route_roads = original_roads
    road_index = 0
    stop_index = 0
    running = True
    mode = 'original'  # TODO: if different start point on altered route, start in altered mode
    while running:
        if mode == 'original':
            current_stop = original_stops[stop_index]
            print(current_stop, stops[current_stop[:4]]['name'])
            stop_index += 1
            next_stop = None
            aval_stops = connections[current_stop]

            # If only one stop is available, then skip and dont bother
            # we assume our connections and og_stops are the same and dont check it here
            if len(aval_stops) == 1:
                continue

            # There are multiple options:

            # Check if any aval_stop is on altered road
            for s in aval_stops:
                print('   ', s, stops[s[:4]]['name'], altered_roads[alt_index], road_matrix[s])
                if altered_roads[alt_index] == road_matrix[s]:
                    print('Success - found alt road', altered_roads[alt_index])
                    # We are now on altered route
                    mode = 'altered'
                    ending_stops = original_stops[stop_index:]
                    print('====')
                    break

            # If no aval_stop is on our alt roads, then search recursively for few stops deep to find alt_road
            success, route = searcher(current_stop, target_road=altered_roads[alt_index], recursion_depth=4)
            if not success:
                print('  Cant find', altered_roads[alt_index], 'recursively, continuing...')
                continue
            else:
                print('Success - found alt road', altered_roads[alt_index], 'recursively')
                # We are now on altered route
                mode = 'altered'
                ending_stops = original_stops[stop_index:] 
                print('====')

        elif mode == 'altered':
            current_route = original_stops[:stop_index] + route[1:]
            mode = 'altered_continue'
        elif mode == 'altered_continue':
            # time.sleep(1)
            skip = False  # this is a mystery variable that will help us later

            current_stop = current_route[-1]
            if current_stop == '100606':
                print('wat the program doin')

            # Do we leave altered mode?
            if current_stop in ending_stops:
                print('We are done here')
                running = False

            print('Route:', current_route)
            print('Currently on:', altered_roads[alt_index])

            aval_stops = connections[current_stop]
            print('Available stops:')
            print(aval_stops)

            # Now, if only one connection is avaliable, take it
            if len(aval_stops) == 1:
                current_route.append(aval_stops[0])
                # print(current_route)
                # Check if road has changed
                if road_matrix[aval_stops[0]] == altered_roads[alt_index]:  # road stays the same
                    pass
                elif road_matrix[aval_stops[0]] == altered_roads[alt_index+1]:  # road has changed to next one
                    alt_index += 1
                else:  # road has changed to something we dont want, but we will ignore and hope it soon changes to what we want
                    print('uh oh unwanted road')
                    pass

                continue
            
            # If more then one is available see if any is on original route
            for s in aval_stops:
                if s in ending_stops:
                    print('We are done here, calling from fork')
                    cut = ending_stops.index(s)
                    print(current_route + ending_stops[cut:])
                    return current_route + ending_stops[cut:]
                    # print(s, ending_stops)
                    running = False

            # If we havent left, see if any are on our next road
            print('  Now looking for (normally):', altered_roads[alt_index+1])
            candidates = []
            for s in aval_stops:
                print('   ', altered_roads[alt_index+1], road_matrix[s])
                if compare(altered_roads[alt_index+1], road_matrix[s]):
                    # In case 2 options pop up
                    candidates.append(s)

            if len(candidates) == 1:
                print('  Success - found alt road', altered_roads[alt_index+1])
                alt_index += 1
                current_route.append(candidates[0])
                skip = True
            elif len(candidates) == 0:
                pass
            else:  # we have two (or more) option with same street. Usually happens bc of T-junctions
                # Solution: Go recursively over each until we find next road lol
                # but first check if there is next road
                if len(altered_roads) <= alt_index+2:
                    # this is last road. instead of looking for next road lets look for next stop
                    print('  Many options:', candidates, '- beginning recursive search until stops', ending_stops)
                    search_type = 'stops'
                else:
                    print('  Many options:', candidates, '- beginning recursive search until street', altered_roads[alt_index+2])
                    search_type = 'streets'

                trying = True  # outer break
                for step in RECURSION_STEPS:
                    if not trying:
                        break
                    for s in candidates:
                        if search_type == 'streets':
                            suc, route = searcher(s, target_road=altered_roads[alt_index+2], recursion_depth=step)
                        elif search_type == 'stops':
                            suc, route = searcher(s, target_stops=ending_stops, recursion_depth=step)

                        if suc:
                            trying = False
                            break

                    if suc:
                        print('  Found answer with option', s, route)
                        alt_index += 2
                        current_route += route
                        if search_type == 'stops':
                            print('We are done here, calling from candidates')
                            cut = ending_stops.index(route[-1])
                            print(current_route + ending_stops[cut:])
                            return current_route + ending_stops[cut:]
                        break

            # If no road still, lets trey recursive search?
            if not skip:
                print('  Now looking for (recursiv):', altered_roads[alt_index+1])
                success, route = searcher(current_stop, target_road=altered_roads[alt_index+1], recursion_depth=4)
                if not success:
                    print('  Cant find', altered_roads[alt_index+1], 'recursively, continuing along current road')
                else:
                    print('  Success - found alt road', altered_roads[alt_index+1], 'recursively')
                    current_route += route[1:]
                    print('  ', current_route)
                    skip = True


            # If no road still, continue on current road
            if not skip:
                print('  Now looking to continue along:', altered_roads[alt_index])
                for s in aval_stops:
                    print('   ', altered_roads[alt_index], road_matrix[s])
                    if altered_roads[alt_index] == road_matrix[s]:
                        print('  Success - found current road at', s)
                        current_route.append(s)
                        skip = True
                        break

# print(searcher('107803', 'Jagiellońska', 9))

# print(connections["708904"])
# print(connections["V001"])

if __name__ == '__main__':
    print(main(original_stops, original_roads, altered_roads))
