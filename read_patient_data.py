import copy
import csv
import os
import re
import sys
from typing import List, Tuple, Iterable

__version__ = 0.01

Visit = List[str]
Encounters = List[Visit]


LBS_PATTERN = re.compile(r"\d+\.?\d+\s*lbs")
HEIGHT_PATTERN = re.compile(r"\d+'\d+|\d+\s*cm")
SMOKE_PATTERN = re.compile(r"[sS]moker[:|\s*][-|\s*]")
FLOAT_PATTERN = re.compile(r"\d+.?\d+")

# TODO: alcohol - split / look to left for a number -- servings


def _yield_from_rows(encounters: Encounters) -> Iterable[str]:
    """Yields each row from all encounters from recent to oldest."""
    for visit in encounters:
        for row in visit:
            yield row


def get_hemoglobin_a1c(encounters: Encounters) -> float:
    """Returns the latest A1c reading."""
    for row in _yield_from_rows(encounters):
        if 'a1c' in row.lower():
            floats = re.findall(FLOAT_PATTERN, row)
            if floats:
                return float(floats[0])
    return 0.0


def has_insurance(encounters: Encounters) -> str:
    """If `Insurance:` key found return the text after the key."""
    for row in _yield_from_rows(encounters):
        if "Insurance:" in row:
            details = row.split("Insurance:")
            if len(details) > 1:
                return details[1].strip()


# def is_alcohol(groups: Encounters) -> bool:
#     """
#     Problem determining specifics as there are many entry types, no two the same.
#     Multiple descriptions throughout reports.
#     Will need further review/discussion.
#     """
#     for group in groups:
#         for line in group:
#             if "alcohol" in line.lower():
#                 print(line)


def get_fasting_glucose(encounters: Encounters) -> float:
    for row in _yield_from_rows(encounters):
        if "fasting" in row.lower():
            result = re.findall(FLOAT_PATTERN, row)
            if result:
                return float(result[0])
    return 0.0


def is_smoker(encounters: Encounters) -> bool:

    for row in _yield_from_rows(encounters):
        smoker = re.findall(SMOKE_PATTERN, row)
        if smoker and "yes" in row.lower():
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


def _get_weights_for_group(visit: Visit) -> Tuple[float, float, float]:
    # today, peak, intake
    a, b, c = 0.0, 0.0, 0.0
    for line in visit:
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


def split_into_encounters(lines: List[str]) -> Encounters:
    encounters = []
    visit = []
    for line in lines:
        visit.append(line)
        if line.startswith("ID:"):
            if len(visit) > 2:
                encounters.append(copy.deepcopy(visit))
                visit = visit[-2:]
    if visit:
        encounters.append(visit)
    return encounters


def find_height(encounters: Encounters) -> Tuple[int, int]:
    heights = []
    for row in _yield_from_rows(encounters):
        results = re.findall(HEIGHT_PATTERN, row)
        if results:
            heights += results
    height, discrepancy = normalize_height(heights)
    return height, discrepancy


def calculate_bmi(height_cm: int, weight_lbs: float) -> float:
    """Returns weight in KGs to 1 decimal place."""
    kilos = weight_lbs / 2.205
    meters = height_cm / 100
    return round(kilos / meters**2, 1)


def get_recent_intake_dates(visit: Visit) -> Tuple[str, str]:
    dates = [line.split()[2] for line in visit if line.startswith("Visit Date:")]
    DEFAULT = "0000-00-00"
    recent, intake = DEFAULT, DEFAULT
    if len(dates) >= 2:
        recent = dates[0]
        intake = dates[-1]
    return recent, intake


def get_weights(encounters: Encounters) -> Tuple[float, float, float]:
    max_weight = 0.0
    min_weight = sys.maxsize
    intake_weights = set()
    for visit in encounters:
        weights = _get_weights_for_group(visit)
        if max(weights) > max_weight:
            max_weight = max(weights)
        if 0 < min(weights) < min_weight:
            min_weight = min(weights)
        if weights[2] != 0.0:
            intake_weights.add(weights[2])
    return max(intake_weights) if intake_weights else 0.0, max_weight, min_weight


def main():
    datasheets = []

    for file in os.listdir("."):
        if file.endswith(".txt"):
            datasheet = {}
            with open(file) as handle:

                lines = handle.readlines()
                encounters = split_into_encounters(lines)

                # start collecting data across the encounters
                intake_weight, max_weight, min_weight = get_weights(encounters)
                height, discrepancy = find_height(encounters)

                recent_date, intake_date = get_recent_intake_dates(lines)
                datasheet["MRN"] = os.path.splitext(file)[0]
                datasheet["Encounters"] = len(encounters)
                datasheet["Recent Visit Date"] = recent_date
                datasheet["Intake Visit Date"] = intake_date
                datasheet["Intake WeightLBS"] = intake_weight
                datasheet["Max WeightLBS"] = max_weight
                datasheet["Min WeightLBS"] = min_weight
                datasheet["HeightCM"] = height
                datasheet["Height_Low_Err"] = discrepancy
                datasheet["Intake BMI"] = calculate_bmi(height, intake_weight)
                datasheet["Max BMI"] = calculate_bmi(height, max_weight)
                datasheet["Min BMI"] = calculate_bmi(height, min_weight)
                datasheet["Smoker"] = is_smoker(encounters)
                datasheet["Insurance"] = has_insurance(encounters)
                datasheet["Fasting Glucose"] = get_fasting_glucose(encounters)
                datasheet["A1c%"] = get_hemoglobin_a1c(encounters)
            datasheets.append(copy.deepcopy(datasheet))

    return datasheets


if __name__ == "__main__":
    datasheets = main()
    if datasheets:
        with open("patient_data.csv", "w") as handle:
            w = csv.DictWriter(handle, datasheets[0].keys())
            w.writeheader()
            for ds in datasheets:
                w.writerow(ds)
