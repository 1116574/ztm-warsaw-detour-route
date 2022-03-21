import json
import time

# 20
original_roads = 'ŻERAŃ FSO - Jagiello\u0144ska - Targowa - al.\"Solidarno\u015bci\" - M\u0142ynarska - Obozowa - Dywizjonu 303 - Gen.Kaliskiego - BOERNEROWO'.split(' - ')[1:-1]
altered_roads = 'ŻERAŃ FSO - … - most Gdański - Słomińskiego - Okopowa - … - BOERNEROWO'.split(' - ')[1:-1]
og_index = 0
alt_index = 1
current_stop = '101305'

# 4
original_roads = 'ŻERAŃ WSCH. - Annopol - Rembieli\u0144ska - Matki Teresy z Kalkuty - Odrow\u0105\u017ca - 11 Listopada - al.\"Solidarno\u015bci\" - pl.Bankowy - Marsza\u0142kowska - Pu\u0142awska - WYŚCIGI'.split(' - ')[1:-1]
altered_roads = 'ŻERAŃ WSCH. - … - Jagiellońska - most Gdański - Słomińskiego - al. Jana Pawła II - Chałubińskiego - Nowowiejska - … - WYŚCIGI'.split(' - ')[1:-1]
og_index = 0
alt_index = 1  # since '...' is start
current_stop = '109101'

# route_roads stores currently relevant roads, depending on the context, same for index
route_roads = original_roads
road_index = 0

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)

with open('trams.json', 'r') as f:
    connections = json.load(f)

with open('road_matrix.json', 'r') as f:
    road_matrix = json.load(f)

recreation = []

MAX_DEPTH = 6
GO_HOME = False  # ?
ALTERED = False

def searcher(current_stop, road_index, recursion_depth, indent, special=False, looking_for_road=None, looking_for_stop=None, route_roads=route_roads):  # special is for prime instance
    alt_index = 1
    recreation = []
    ALTERED = False
    while recursion_depth:
        CHECKS = True
        # for recursed calls:
        # Check if we found our road
        if looking_for_road == road_matrix[current_stop]:
            print(f'<{indent[:-1]} Found target road! returning {recreation}')
            return recreation

        # Keep track if we are on altered or original route
        # if route_roads[road_index] == '…' and ALTERED == False:  
        #     # idk if we need this
        #     ALTERED = True

        print(indent, recreation)
        recursion_depth -= 1
        print(f'{indent}------{recursion_depth}')
        print(indent, route_roads[road_index])
        print(indent, current_stop, stops[current_stop[:4]]['name'], road_matrix[current_stop])

        available_connections = connections[current_stop]
        print(f'{indent}  connections: {available_connections}')
        if len(available_connections) == 1:
            next_stop = available_connections[0]
            next_road = road_matrix[next_stop]
            print(f'{indent}  selecting only option {available_connections} on road {next_road}')
            # Check if next_stop is on good road
            if route_roads[road_index] == next_road:
                # roads are the same, do nothing
                pass
            elif route_roads[road_index + 1] == next_road:
                # roads are different, but adhere to route
                road_index += 1
                print(f'{indent}  road has changed to: {next_road}')
            elif route_roads[road_index + 1] == '…':
                # we dont know what next road is supposded to be, but since we have no choice
                road_index += 1
                print(f'{indent}  road changed to ...')

            elif route_roads[road_index] == '…':
                print(f'{indent}  road is ...')
                # we dont actually know what road are we supposed to be,
                # so we look on original route and altered one,
                # and we try deducing if we are clear of alteration? TODO?
                pass

            recreation.append(current_stop)
            current_stop = next_stop
            continue

        # print(f'{indent}  branching')
        # 1. Firstly try finding roads that are on our altered route, and if so change altered with original
        # 2. same, but recursively (we need to check EVERY branch for atleast {MAX_DEPTH}
        #    and searh for new streets there. This is bc ZTM sometimes skips roads that run for few (<4) stops)
        # 3. If alt roads cant be found, try looking for og roads
        # 4. same, but with recursion (even tho its not needed?)
        # 5. If we are in alt route, and on '...' try looking for og road to change back to normal route
        # 6. If we dont find any, then look for street that is on same road as we are now
        

        # (1.)
        print(f'{indent}  looking for roads from altered route  {altered_roads[1]}')
        for next_stop in available_connections:
            next_road = road_matrix[next_stop]
            print(f'{indent}    - ', next_stop, stops[next_stop[:4]]['name'], next_road)
            if next_road == altered_roads[1]:  # index 0 is '...', so 1 is the actual road
                print(f'{indent}  found altered road: {next_road} , changing route_roads')
                print(f'{indent} === CHANGING ROUTE_ROADS ===')
                route_roads = altered_roads
                og_index = road_index  # save for later i guess?
                alt_index += 1
                road_index = alt_index
                ALTERED = True
                CHECKS = False

                recreation.append(current_stop)
                current_stop = next_stop
                time.sleep(5)
                break

        # (2.)
        if CHECKS and not ALTERED:
            print(f'{indent}  branching recursively until we find road {altered_roads[alt_index]}')
            for next_stop in available_connections:
                time.sleep(1)
                if special:
                    found = searcher(next_stop, road_index, MAX_DEPTH, indent + '|', looking_for_road=altered_roads[1])
                else:
                    found = searcher(next_stop, road_index, recursion_depth, indent + '|', looking_for_road=altered_roads[1])
                    return found

                if found:
                    print(f'{indent} Succesfully recived {found}')
                    print(f'{indent} === CHANGING ROUTE_ROADS ===')
                    print(f'{indent} Now aborting further searches and changing route to alt')
                    route_roads = altered_roads
                    og_index = road_index  # save for later i guess?
                    road_index = alt_index
                    ALTERED = True
                    CHECKS = False

                    recreation.append(current_stop)
                    current_stop = next_stop
                    time.sleep(5)
                    break

        # (3.)
        if CHECKS:
            print(f'{indent}  branching for new roads')
            for next_stop in available_connections:
                next_road = road_matrix[next_stop]
                print(f'{indent}    - ', next_stop, stops[next_stop[:4]]['name'], next_road)
                if next_road == route_roads[road_index + 1]:
                    print(f'{indent}    ^ selecting')
                    recreation.append(current_stop)
                    current_stop = next_stop
                    # continue
                    break

        # (4.)
        # print(f'{indent}  branching recursively until we find {route_roads[road_index + 1]}')
        if CHECKS:
            # if route_roads[road_index] == '…':
            print(f'{indent}  branching recursively until we find road {route_roads[road_index + 1]}')
            for next_stop in available_connections:
                time.sleep(1)
                if special:
                    found = searcher(next_stop, road_index, MAX_DEPTH, indent + '|', looking_for_road=route_roads[road_index + 1])
                else:
                    found = searcher(next_stop, road_index, recursion_depth, indent + '|', looking_for_road=route_roads[road_index + 1])
                    return found

                if found:
                    print(f'{indent} Succesfully recived {found}')
                    print(f'{indent} Now aborting further searches and appending to recreation')
                    CHECKS = False  # we use this so we can skip 3. and 4.
                    recreation.extend(found[:-1])
                    current_stop = found[-1]
                    road_index += 1
                    break



        # (5.)
        if CHECKS and ALTERED:  # basically if 2. finds something, skip 3. and 4.
            print(f'{indent}  looking for og roads to go home, since we are in altered route')
            for next_stop in available_connections:
                next_road = road_matrix[next_stop]
                print(f'{indent}    - ', next_stop, stops[next_stop[:4]]['name'], next_road)
                if next_road in original_roads:
                    print(f'{indent}  Found og road {next_road}')
                    # NOTE: something about direction of track? but i think its ensured already by `connections`
                    recreation.append(current_stop)
                    recreation.append(next_stop)  # ?
                    # Now we switch to original timetable, so either we break out or still do a route? idk
                    # GO_HOME = True

                    # ### VERY TESING ###
                    # swiching timetables and indexes
                    # print(f'{indent} SWITCHING TIMETABLES')
                    # time.sleep(5)
                    # road_index  = original_roads.index(next_road)
                    # route_roads = original_roads
                    # current_stop = next_stop

                    return recreation
                    # # # continue
                    # ALTERED = False  # we can go 'back' only once
                    # CHECKS = False  # skip next step
                    # break

        # (6.)
        if CHECKS:
            print(f'{indent}  branching for current road')
            for next_stop in available_connections:
                next_road = road_matrix[next_stop]
                print(f'{indent}    - ', next_stop, stops[next_stop[:4]]['name'], next_road)
                if next_road == route_roads[road_index]:
                    print(f'{indent}    ^ selecting')
                    recreation.append(current_stop)
                    current_stop = next_stop
                    continue

        time.sleep(1)

    return False

pass
result = searcher(current_stop, road_index, 80, '|', special=True)

print('=====')
print(result)