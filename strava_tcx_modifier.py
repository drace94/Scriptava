# -*- coding: utf-8 -*-

import numpy as np

def read_tcx(file_tcx) :
    lines = []
    
    with open(file_tcx, 'r') as file:
        lines = file.readlines()
    
    return lines

def write_tcx(file_tcx, lines) :

    with open(file_tcx, 'w') as file:
        for line in lines:
            file.write(line)

file_path = 'activity.tcx'
lines_tcx = read_tcx(file_path)

index_start_tracking = 0
index_end_tracking = 0
start_time = 0
for i, line in enumerate(lines_tcx):
    if line.strip() == '<Track>' :
        index_start_tracking = i
        print("Found start of tracking")
    elif line.strip()[38:] == '0Z">':
        start_time = int(line.strip()[33:35])
    elif line.strip() == '</Track>' :
        index_end_tracking = i
        print("Found end of tracking")
        break

dist = 0
v = 25000. / 3600. # m.s^-1
time = 0
old_time = start_time
for pos, line in enumerate(lines_tcx[index_start_tracking:index_end_tracking]):
    if line.strip() == '<Trackpoint>' :
        pos_time = pos + 1
        
        dt = int(lines_tcx[pos_time + index_start_tracking].strip()[23:25]) - old_time
        time += dt * (dt > 0) + (dt + 60) * (dt < 0)
        old_time = int(lines_tcx[pos_time + index_start_tracking].strip()[23:25])
    
        dist = v * time + np.random.normal(0.0,1e-1)
        
        pos_dist = pos + 2
        string_dist = str(dist)
        # for i, character in enumerate(string_dist) :
        #     if character == '.':
        #         pos_dot = i
        #         break
            
        # string_dist = string_dist[:pos_dot+2]
        new_line = '            <DistanceMeters>' + string_dist + '</DistanceMeters>' + '\n'
        lines_tcx[index_start_tracking + pos_dist] = new_line

lines_tcx[13] = '        <DistanceMeters>' + string_dist + '</DistanceMeters>' + '\n'

write_tcx('clean.tcx', lines_tcx)

        