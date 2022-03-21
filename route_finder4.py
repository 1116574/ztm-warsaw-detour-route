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
og_index = 0
alt_index = 0

# 4
original_stops = ["109101","109001","108903","108803","108603","108503","108401","108303","108201","108003","107903","107803","107703","107101","106603","100303","116301","704702","709910","701607","701505","701405","701307","701203","701105","701003","708001","300105","300205","300305","300403","300505","300605","300703","300803","300905","301003","301107","301206"]
original_roads = 'ŻERAŃ WSCH. - Annopol - Rembieli\u0144ska - Matki Teresy z Kalkuty - Odrow\u0105\u017ca - 11 Listopada - al.\"Solidarno\u015bci\" - pl.Bankowy - Marsza\u0142kowska - Pu\u0142awska - WYŚCIGI'.split(' - ')[1:-1]
altered_roads = 'ŻERAŃ WSCH. - … - Jagiellońska - most Gdański - Słomińskiego - al. Jana Pawła II - Chałubińskiego - Nowowiejska - … - WYŚCIGI'.split(' - ')[2:-2]
og_index = 0
alt_index = 0

# route_roads stores currently relevant roads, depending on the context, same for index
route_roads = original_roads
road_index = 0

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)

with open('trams.json', 'r') as f:
    connections = json.load(f)

with open('manual_connections.json', 'r') as f:
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

### Recursive search
def searcher(current_stop, target_road, recursion_depth, max_print=8):
    # print('|'*(max_print-recursion_depth), recursion_depth)
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
            # Spawn new string
            suc, tmp = searcher(c, target_road, recursion_depth-1)
            route += tmp
            if suc:
                return True, route
    except KeyError:
        pass


    return False, []

### MAIN
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
        time.sleep(1)
        skip = False  # this is a mystery variable that will help us later

        current_stop = current_route[-1]

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
                running = False

        # If we havent left, see if any are on our next road
        print('  Now looking for (normally):', altered_roads[alt_index+1])
        for s in aval_stops:
            print('   ', altered_roads[alt_index+1], road_matrix[s])
            if altered_roads[alt_index+1] == road_matrix[s]:
                alt_index += 1
                print('  Success - found alt road', altered_roads[alt_index])
                current_route.append(s)
                skip = True
                break

        # If no road still, lets trey recursive search?
        if not skip:
            print('  Now looking for (recursiv):', altered_roads[alt_index+1])
            success, route = searcher(current_stop, target_road=altered_roads[alt_index+1], recursion_depth=4)
            if not success:
                print('  Cant find', altered_roads[alt_index+1], 'recursively, continuing along current road')
            else:
                print('  Success - found alt road', altered_roads[alt_index+1], 'recursively')
                current_route += route
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