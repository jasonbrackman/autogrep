import copy
import csv

import os
import re
import sys
from typing import List, Tuple, Set

PATTERN = re.compile("\d+")
HEIGHT_PATTERN = re.compile("\d+'\d+|\d+\s?cm")


def normalize_height(heights: List[str]) -> Tuple[int, int]:
    INCHES_TO_CMS = 2.54
    new_heights = set()
    for height in heights:
        height = height.replace("cm", "").strip()
        height = height.replace('"', "")
        feet_inches = height.split("'")
        if len(feet_inches) == 2:
            feet, inches = feet_inches
            feet = float(feet.strip()) * 12
            inches = float(inches.strip())
            height = (feet + inches) * INCHES_TO_CMS

        else:
            height = int(height.strip())
        new_heights.add(round(height))
    low = min(new_heights)
    high = max(new_heights)
    return high, high - low


def get_group_weight(group: List[str]) -> Tuple[float, float, float]:
    # today, peak, intake
    a, b, c = 0.0, 0.0, 0.0
    for line in group:
        if line.startswith("Today's Weight:"):
            temp = re.findall(PATTERN, line)
            if temp:
                a = temp[0]
        elif line.startswith("Peak Adult Weight:"):
            temp = re.findall(PATTERN, line)
            if temp:
                b = temp[0]
        elif line.startswith("Intake Weight:"):
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


def find_height(groups: List[list[str]]) -> Tuple[int, int]:
    heights = []
    for group in groups:
        for line in group:
            results = re.findall(HEIGHT_PATTERN, line)
            if results:
                heights += results
    height, discrepancy = normalize_height(heights)
    return height, discrepancy


def main():
    datasheets = []

    for file in os.listdir("."):
        if file.endswith(".txt"):
            datasheet = {}
            with open(file) as handle:

                lines = handle.readlines()
                groups = split_into_groups(lines)

                # start collecting data across the groups
                intake_weights, max_weight, min_weight = get_weights(groups)
                height, discrepancy = find_height(groups)

                recent_date, intake_date = get_recent_intake_dates(lines)
                datasheet["Patient Number"] = os.path.splitext(file)[0]
                datasheet["Encounters"] = len(groups)
                datasheet["Recent Visit Date"] = recent_date
                datasheet["Intake Visit Date"] = intake_date
                datasheet["Intake Weight"] = max(intake_weights)  # possible duplicate entries
                datasheet["Max Weight"] = max_weight
                datasheet["Min Weight"] = min_weight
                datasheet["HeightCM"] = height
                datasheet["Height_Low_Err"] = discrepancy
                datasheet["Intake BMI"] = calculate_bmi(height, datasheet['Intake Weight'])
                datasheet["Max BMI"] = calculate_bmi(height, max_weight)
                datasheet["Min BMI"] = calculate_bmi(height, min_weight)

            datasheets.append(copy.deepcopy(datasheet))

    return datasheets


def calculate_bmi(height_cm: int, weight_lbs: float) -> float:
    """Returns weight in KGs to 1 decimal place."""
    kilos = weight_lbs / 2.205
    meters = height_cm / 100
    return round(kilos / meters**2, 1)


def get_recent_intake_dates(lines: List[str]) -> Tuple[str, str]:
    dates = [
        line.split()[2] for line in lines if line.startswith("Visit Date:")
    ]
    DEFAULT = '0000-00-00'
    recent, intake = DEFAULT, DEFAULT
    if len(dates) >= 2:
        recent = dates[0]
        intake = dates[-1]
    return recent, intake


def get_weights(groups):
    max_weight = 0.0
    min_weight = sys.maxsize
    intake_weights = set()
    for group in groups:
        weights = get_group_weight(group)
        if max(weights) > max_weight:
            max_weight = max(weights)
        if 0 < min(weights) < min_weight:
            min_weight = min(weights)
        if weights[2] != 0.0:
            intake_weights.add(weights[2])
    return intake_weights, max(intake_weights), min(intake_weights)


if __name__ == "__main__":
    datasheets = main()
    if datasheets:
        with open("patient_data.csv", "w") as handle:
            w = csv.DictWriter(handle, datasheets[0].keys())
            w.writeheader()
            for ds in datasheets:
                w.writerow(ds)
