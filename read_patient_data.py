import copy

import os
import re
import sys
from typing import List, Tuple

PATTERN = re.compile('\d+')


def get_group_weight(group: List[str]) -> Tuple[float, float, float]:
    a, b, c = 0.0, 0.0, 0.0
    for line in group:
        if line.startswith("Today's Weight"):
            temp = re.findall(PATTERN, line)
            if temp:
                a = temp[0]
        elif line.startswith("Peak Adult Weight"):
            temp = re.findall(PATTERN, line)
            if temp:
                b = temp[0]
        elif line.startswith("Intake Weight"):
            temp = re.findall(PATTERN, line)
            if temp:
                c = temp[0]

    return float(a), float(b), float(c)

def split_into_groups(lines: List[str]) -> List[List[str]]:
    groups = []
    temp = []
    for line in lines:
        temp.append(line)
        if line.startswith("ID:"):
            if len(temp) > 2:
                groups.append(copy.deepcopy(temp))
                temp = temp[-2:]
    if temp:
        groups.append(temp)
    return groups

datasheets = []

for file in os.listdir('.'):
    datasheet = {
        'Patient Number': 0,
        'Encounters': 0,
        'Recent Visit Date': 0000-00-00,
        'Intake Visit Date': 0000-00-00,
        'Max Weight': 0.0,
        'Min Weight': 0.0,
    }

    if file.endswith('.txt'):
        with open(file) as handle:

            lines = handle.readlines()
            groups = split_into_groups(lines)

            max_weight = 0.0
            min_weight = sys.maxsize
            for group in groups:
                weights = get_group_weight(group)
                if max(weights) > max_weight:
                    max_weight = max(weights)
                if 0 < min(weights) < min_weight:
                    min_weight = min(weights)

            all_dates = [line.split()[2] for line in lines if line.startswith("Visit Date:")]
            datasheet['Patient Number'] = file
            datasheet['Encounters'] = len(groups)
            datasheet['Recent Visit Date'] = all_dates[0]
            datasheet['Intake Visit Date'] = all_dates[-1]
            datasheet['Max Weight'] = max_weight
            datasheet['Min Weight'] = min_weight


        datasheets.append(datasheet)


#
# for ds in datasheets:
#     for k, v in ds.items():
#         print(f'{k}: {v}')
#     x = json.dumps(ds)
#     with open(ds['Patient Number'].replace('.txt', '.json'), 'w') as handle:
#         handle.write(x)
#
#     with open(ds['Patient Number'].replace('.txt', '.csv'), 'w') as handle:
#         w = csv.DictWriter(handle, ds.keys())
#         w.writeheader()
#         w.writerow(ds)
