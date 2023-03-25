import copy
import csv
import os
import re
import sys
from typing import List, Tuple

LBS_PATTERN = re.compile(r"\d+\.?\d+\s*lbs")
HEIGHT_PATTERN = re.compile(r"\d+'\d+|\d+\s*cm")
SMOKE_PATTERN = re.compile(r"[sS]moker[:|\s*][-|\s*]")
# TODO:
# --> Fasting Glucose / Glucose Fasting: + float
# --> HBA1c / Hemoglobin (always a1c): + float
# --> alcohol - split / look to left for a number -- servings


def has_insurance(groups: List[List[str]]) -> str:
    """If `Insurance:` key found return the text after the key."""
    for group in groups:
        for line in group:
            if "Insurance:" in line:
                details = line.split("Insurance:")
                if len(details) > 1:
                    return details[1].strip()


# def is_alcohol(groups: List[List[str]]) -> bool:
#     """
#     Problem determining specifics as there are many entry types, no two the same.
#     Multiple descriptions throughout reports.
#     Will need further review/discussion.
#     """
#     for group in groups:
#         for line in group:
#             if "alcohol" in line.lower():
#                 print(line)


def is_smoker(groups: List[List[str]]) -> bool:
    for group in groups:
        for line in group:
            smoker = re.findall(SMOKE_PATTERN, line)
            if smoker and "yes" in line.lower():
                return True
    return False


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


def _get_weights_for_group(group: List[str]) -> Tuple[float, float, float]:
    # today, peak, intake
    a, b, c = 0.0, 0.0, 0.0
    for line in group:
        temp = re.findall(LBS_PATTERN, line)
        if temp:
            temp = temp[0].replace("lbs", "").strip()
            if line.startswith("Today's Weight:"):
                a = temp
            elif line.startswith("Peak Adult Weight:"):
                b = temp
            elif line.startswith("Intake Weight:"):
                c = temp

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


def calculate_bmi(height_cm: int, weight_lbs: float) -> float:
    """Returns weight in KGs to 1 decimal place."""
    kilos = weight_lbs / 2.205
    meters = height_cm / 100
    return round(kilos / meters**2, 1)


def get_recent_intake_dates(lines: List[str]) -> Tuple[str, str]:
    dates = [line.split()[2] for line in lines if line.startswith("Visit Date:")]
    DEFAULT = "0000-00-00"
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
        weights = _get_weights_for_group(group)
        if max(weights) > max_weight:
            max_weight = max(weights)
        if 0 < min(weights) < min_weight:
            min_weight = min(weights)
        if weights[2] != 0.0:
            intake_weights.add(weights[2])
    return max(intake_weights), max_weight, min_weight


def main():
    datasheets = []

    for file in os.listdir("."):
        if file.endswith(".txt"):
            datasheet = {}
            with open(file) as handle:

                lines = handle.readlines()
                groups = split_into_groups(lines)

                # start collecting data across the groups
                intake_weight, max_weight, min_weight = get_weights(groups)
                height, discrepancy = find_height(groups)

                recent_date, intake_date = get_recent_intake_dates(lines)
                datasheet["Patient Number"] = os.path.splitext(file)[0]
                datasheet["Encounters"] = len(groups)
                datasheet["Recent Visit Date"] = recent_date
                datasheet["Intake Visit Date"] = intake_date
                datasheet["Intake Weight"] = intake_weight
                datasheet["Max Weight"] = max_weight
                datasheet["Min Weight"] = min_weight
                datasheet["HeightCM"] = height
                datasheet["Height_Low_Err"] = discrepancy
                datasheet["Intake BMI"] = calculate_bmi(height, intake_weight)
                datasheet["Max BMI"] = calculate_bmi(height, max_weight)
                datasheet["Min BMI"] = calculate_bmi(height, min_weight)
                datasheet["Smoker"] = is_smoker(groups)
                datasheet["Insurance"] = has_insurance(groups)
            datasheets.append(copy.deepcopy(datasheet))

    return datasheets


if __name__ == "__main__":
    datasheets = main()
    if datasheets:
        with open("data/patient_data.csv", "w") as handle:
            w = csv.DictWriter(handle, datasheets[0].keys())
            w.writeheader()
            for ds in datasheets:
                w.writerow(ds)
