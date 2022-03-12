import json

from numpy import r_


# Convert to lists and remove first and last positions since they refer to stop names
#  –  =/= -   # Two different unicode symbols!
changed = 'ŻERAŃ FSO - … - most Gdański - Słomińskiego - Okopowa - … - BOERNEROWO'.split(' - ')[1:-1]
original = 'ŻERAŃ FSO - Jagiello\u0144ska - Targowa - al.\"Solidarno\u015bci\" - M\u0142ynarska - Obozowa - Dywizjonu 303 - Gen.Kaliskiego - BOERNEROWO'.split(' - ')[1:-1]

with open('stop_groups.json', 'r') as f:
    stops = json.load(f)

with open('new_form.json', 'r') as f:
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
while True:
    if r_index > len(original):
        break

    print(first_stop)
    print(stops[first_stop[:4]]['name'])
    if len(new_form[first_stop]) == 1:
        print('Efficiency skipping')
        if road_matrix[first_stop] == original[r_index]:
            # this stop is on correct road, do nothing
            print('  ', first_stop, 'same road', road_matrix[first_stop], original[r_index])
            pass
        else:
            # this stop is on different road
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

    print('Branching')
    # Loop looking for new roads
    for potential_next_stop in new_form[first_stop]:
        print('  n_branch ', potential_next_stop, road_matrix[potential_next_stop])
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
        if road_matrix[potential_next_stop] == original[r_index]:  # still the same street
            print('  selected', potential_next_stop, road_matrix[potential_next_stop])
            recreation.append(first_stop)
            recreation.append(potential_next_stop)
            first_stop = potential_next_stop
            break

    pass                

print(recreation)
