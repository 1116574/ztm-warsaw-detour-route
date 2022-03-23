import json


# Convert to lists and remove first and last positions since they refer to stop names
#  –  =/= -   # Two different unicode symbols!
changed = 'ŻERAŃ FSO - … - most Gdański - Słomińskiego - Okopowa - … - BOERNEROWO'.split(' - ')[1:-1]
original = 'ŻERAŃ FSO - Jagiello\u0144ska - Targowa - al.\"Solidarno\u015bci\" - M\u0142ynarska - Obozowa - Dywizjonu 303 - Gen.Kaliskiego - BOERNEROWO'.split(' - ')[1:-1]

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)

with open('trams.json', 'r') as f:
    new_form = json.load(f)

with open('road_matrix.json', 'r') as f:
    road_matrix = json.load(f)

first_stop = '101305'


print(original)
# First lets try finding original route
recreation = []
# for road in original:
#     if len(new_form[first_stop]) == 1:
#         continue
#     for potential_next_stop in new_form[first_stop]:
#         print(potential_next_stop, road_matrix[potential_next_stop], road)
#         if road_matrix[potential_next_stop] == road:
#             # thats a good stop
#             recreation.append(potential_next_stop)
#             break  # ?

r_index = 0
skip_next = False
last_branch = None
blacklist = []

three_last_stops = ['placeholder1', 'placeholder2', 'placeholder3']

ending_stops = ['505601']
# You are supposed to place all stops from route here that are unchanged
# and start finder from deviating stop

while True:
    if r_index > len(original):
        break

    three_last_stops.append(first_stop)
    if three_last_stops[-1] == three_last_stops[-2] == three_last_stops[-3]:
        print('Loop detected, stopping')
        print(recreation)
        print(first_stop)    
        break

    if first_stop in ending_stops:
        print('Route found and completed')
        print(recreation)

    print(recreation)
    print(first_stop)
    print(stops[first_stop[:4]]['name'])
    if len(new_form[first_stop]) == 1:
        print('Efficiency skipping')
        # Case 1: 'forced' stop is on the same road
        if road_matrix[new_form[first_stop][0]] == original[r_index]:
            print('  ', first_stop, 'same road', road_matrix[first_stop], original[r_index])
            recreation.append(first_stop)
            first_stop = new_form[first_stop][0]
            # Check if next stop doesnt change road
            if road_matrix[first_stop] != original[r_index]:
                # road changed in next stop
                r_index += 1
                print('ABB', road_matrix[first_stop], original[r_index])
            continue
        # Case 2: 'forced' stop is on different road, check if its a good road
        elif road_matrix[new_form[first_stop][0]] == original[r_index + 1]:
            r_index += 1
            # safety
            # assert
            print('AAA', road_matrix[first_stop], original[r_index])
            print('  ', first_stop, 'different road', road_matrix[first_stop], original[r_index])
            recreation.append(first_stop)
            first_stop = new_form[first_stop][0]
            # Check if next stop doesnt change road
            if road_matrix[first_stop] != original[r_index]:
                # road changed in next stop
                r_index += 1
                print('ABB', road_matrix[first_stop], original[r_index])
            continue
        # Case 3: Its both wrong, we need to backtrack to last branch
        else:
            for i in range(len(recreation)):
                removed = recreation.pop()
                blacklist.append(removed)
                if removed == last_branch:
                    first_stop = removed
                    break



    print('Branching')
    last_branch = first_stop
    # Loop looking for new roads
    for potential_next_stop in new_form[first_stop]:
        print('  n_branch ', potential_next_stop, road_matrix[potential_next_stop])
        if potential_next_stop in blacklist:
            print('  ^n_blacklisted')
            continue

        if road_matrix[potential_next_stop] == original[r_index + 1]:  # new street
            print('  n_selected', potential_next_stop, road_matrix[potential_next_stop])
            # correct branch
            r_index += 1
            recreation.append(first_stop)
            recreation.append(potential_next_stop)
            first_stop = potential_next_stop
            skip_next = True
            break

    if skip_next:
        skip_next = False
        continue

    # If no new roads, loop to see if any old roads remain
    for potential_next_stop in new_form[first_stop]:
        print('  branch ', potential_next_stop, road_matrix[potential_next_stop])
        if potential_next_stop in blacklist:
            print('  ^blacklisted')
            continue

        if road_matrix[potential_next_stop] == original[r_index]:  # still the same street
            print('  selected', potential_next_stop, road_matrix[potential_next_stop])
            recreation.append(first_stop)
            recreation.append(potential_next_stop)
            first_stop = potential_next_stop
            break

    pass                

print(recreation)
